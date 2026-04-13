// 동네마켓 좌측 지도 위젯 (내 위치 + 키워드/카테고리 검색 핀 표시)
// - lm_ 접두사로 id 충돌 방지
// - 기존 벼룩시장 기능은 건드리지 않음

(function () {
  const CFG = window.LOCAL_MARKET_CONFIG || {};
  const $ = (id) => document.getElementById(id);

  const elMap = $("lm_map");
  const elAddr = $("lm_current_addr");
  const elKeyword = $("lm_keyword");
  const elResult = $("lm_result");
  const btnSearch = $("lm_btn_search");
  const btnMyLoc = $("lm_btn_myloc");
  const quickBtns = document.querySelectorAll(".lm-quick");

  if (!elMap) return;

  let map = null;
  let ps = null;
  let geocoder = null;

  let markers = [];       // 장소 검색 마커
  let overlay = null;     // 열려있는 오버레이 1개 유지
  let fleaMarkers = [];   // 벼룩상품 마커들

  let myLat = null;
  let myLng = null;
  // ✅ 거리 계산 기준점(내 주소/내 위치 마지막 기준)
  let baseLat = null;
  let baseLng = null;

  // 반경 표시(원/중심마커) 중복 방지
  let radiusCircle = null;
  let radiusCenterMarker = null;

  function setAddrText(text) {
    if (!elAddr) return;
    elAddr.textContent = text;
  }

  function clearMarkers() {
    markers.forEach((m) => m.setMap(null));
    markers = [];
  }

  function clearFleaMarkers() {
    fleaMarkers.forEach((m) => m.setMap(null));
    fleaMarkers = [];
  }

  function closeOverlay() {
    if (overlay) {
      overlay.setMap(null);
      overlay = null;
    }
  }

  function initMap(lat, lng) {
    const center = new kakao.maps.LatLng(lat, lng);
    map = new kakao.maps.Map(elMap, { center, level: 4 });

    ps = new kakao.maps.services.Places();
    geocoder = new kakao.maps.services.Geocoder();
  }

  function centerTo(lat, lng, level) {
    if (!map) return;
    if (typeof level === "number") map.setLevel(level);
    map.panTo(new kakao.maps.LatLng(lat, lng));
  }

  // ✅ 오버레이 잘림/마커 위치 보정: 하단 밖으로 밀리면 off 자동 축소(clamp)
  function panToWithOffset(lat, lng, offsetY) {
    if (!map) return;
    let off = Number(offsetY) || 0;

    const proj = map.getProjection();
    if (!proj) {
      centerTo(lat, lng, 4);
      return;
    }

    const markerPos = new kakao.maps.LatLng(lat, lng);
    const point = proj.containerPointFromCoords(markerPos);

    const mapH = (elMap && elMap.clientHeight) ? elMap.clientHeight : 400;
    const bottomPad = 70;

    const maxOff = Math.max(0, (mapH - bottomPad) - point.y);
    off = Math.max(0, Math.min(off, maxOff));

    point.y -= off;

    const newCenter = proj.coordsFromContainerPoint(point);
    map.setCenter(newCenter);
  }

  function coordToAddr(lat, lng) {
    if (!geocoder) return;
    geocoder.coord2Address(lng, lat, function (result, status) {
      if (status === kakao.maps.services.Status.OK && result && result[0]) {
        const addr =
          (result[0].road_address && result[0].road_address.address_name) ||
          (result[0].address && result[0].address.address_name) ||
          "";
        setAddrText(addr ? `현재 내 위치: ${addr}` : "현재 내 위치");
      } else {
        setAddrText("주소 변환에 실패했어요.");
      }
    });
  }

  function drawRadius(centerLat, centerLng, rkm) {
    if (!map) return;

    if (radiusCircle) radiusCircle.setMap(null);
    if (radiusCenterMarker) radiusCenterMarker.setMap(null);

    const center = new kakao.maps.LatLng(centerLat, centerLng);

    radiusCircle = new kakao.maps.Circle({
      center,
      radius: (Number(rkm) || 0.5) * 500,
      strokeWeight: 2,
      strokeColor: "#ff6b6b",
      strokeOpacity: 0.9,
      strokeStyle: "solid",
      fillColor: "#ff6b6b",
      fillOpacity: 0.15,
    });

    radiusCircle.setMap(map);

    radiusCenterMarker = new kakao.maps.Marker({ position: center });
    radiusCenterMarker.setMap(map);
  }

  function clearRadius() {
    if (radiusCircle) radiusCircle.setMap(null);
    if (radiusCenterMarker) radiusCenterMarker.setMap(null);
    radiusCircle = null;
    radiusCenterMarker = null;
  }

  function loadFleaPins({ lat, lng, rkm }) {
    if (!CFG.fleaPinsApi) return;

    clearFleaMarkers();

    // ✅ 1차: lat/lng 있으면 반경 필터로 요청
    // ✅ 2차: 결과가 0개면 필터 없이 전체 핀 다시 요청(=핀 0개 방지)
    const hasCenter = Number.isFinite(Number(lat)) && Number.isFinite(Number(lng));
    const buildUrl = (useCenter) => {
      if (!useCenter) return CFG.fleaPinsApi;
      const rr = Number.isFinite(Number(rkm)) ? Number(rkm) : 1;
      return (
        CFG.fleaPinsApi +
        `?clat=${encodeURIComponent(lat)}&clng=${encodeURIComponent(lng)}&r=${encodeURIComponent(rr)}`
      );
    };

    const drawPins = (items) => {
      (items || []).forEach((item) => {
        const ilat = Number(item.lat);
        const ilng = Number(item.lng);
        if (!Number.isFinite(ilat) || !Number.isFinite(ilng)) return;

        const marker = new kakao.maps.Marker({
          map,
          position: new kakao.maps.LatLng(ilat, ilng),
        });

        fleaMarkers.push(marker);

        kakao.maps.event.addListener(marker, "click", function () {
          showFleaOverlay(item, ilat, ilng);
        });
      });
    };

    // 1차 요청
    fetch(buildUrl(hasCenter))
      .then((r) => r.json())
      .then((data) => {
        if (!data || !Array.isArray(data.items)) return;

        // ✅ 반경 필터 결과가 0개면 -> 전체 핀으로 재시도
        if (hasCenter && data.items.length === 0) {
          return fetch(buildUrl(false))
            .then((r) => r.json())
            .then((all) => {
              if (!all || !Array.isArray(all.items)) return;
              drawPins(all.items);
            });
        }

        drawPins(data.items);
      })
      .catch(() => {});
  }


  function getSearchCenter() {
    if (myLat != null && myLng != null) return { lat: myLat, lng: myLng };
    if (map) {
      const c = map.getCenter();
      return { lat: c.getLat(), lng: c.getLng() };
    }
    return { lat: 37.5665, lng: 126.9780 };
  }
  // ✅ 숫자 가격 포맷(예: 10000 -> 10,000원)
  function formatPriceKRW(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return (value || "");
    try {
      return n.toLocaleString("ko-KR") + "원";
    } catch (e) {
      return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ",") + "원";
    }
  }

  // ✅ 두 좌표 거리(km) 계산(Haversine)
  function distanceKm(lat1, lng1, lat2, lng2) {
    const R = 6371; // km
    const toRad = (d) => (d * Math.PI) / 180;
    const dLat = toRad(lat2 - lat1);
    const dLng = toRad(lng2 - lng1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
      Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  // ✅ km 표시 문자열
  function formatDistanceKm(km) {
    if (!Number.isFinite(km)) return "";
    if (km < 1) return km.toFixed(1) + "km";
    if (km < 10) return km.toFixed(1) + "km";
    return Math.round(km) + "km";
  }


  // ✅ 회원주소 중심 잡기: (주소+상세) → 실패하면 (주소만) 재시도
  function setCenterFromUserAddress(onSuccess, onFail) {
    const addr = (CFG.defaultAddress || "").trim();
    const detail = (CFG.defaultAddressDetail || "").trim();

    // ✅ 주소가 있으면 일단 표시 (geocoder 검색 전)
    if (addr) {
      setAddrText(`회원 주소: ${addr}`);
    }

    const candidates = [];
    const full = (addr + (detail ? " " + detail : "")).trim();
    if (full) candidates.push({ q: full, label: addr });
    if (addr && full !== addr) candidates.push({ q: addr, label: addr });
    if (!addr && detail) candidates.push({ q: detail, label: detail });

    if (!candidates.length || !geocoder || !map) {
      if (typeof onFail === "function") onFail();
      return false;
    }

    const trySearch = (i) => {
      if (i >= candidates.length) {
        if (typeof onFail === "function") onFail();
        return;
      }

      geocoder.addressSearch(candidates[i].q, function (result, status) {
        if (status === kakao.maps.services.Status.OK && result && result[0]) {
          const lat = Number(result[0].y);
          const lng = Number(result[0].x);

          if (Number.isFinite(lat) && Number.isFinite(lng)) {
            myLat = lat;
            myLng = lng;
            baseLat = lat; baseLng = lng;

            centerTo(lat, lng, 4);
            setAddrText(`회원 주소 기준: ${candidates[i].label}`);

            if (typeof onSuccess === "function") onSuccess(lat, lng);
            return;
          }
        }

        trySearch(i + 1);
      });
    };

    trySearch(0);
    return true;
  }

  function findMyLocation() {
    if (!navigator.geolocation) {
      setAddrText("위치 정보를 지원하지 않는 브라우저입니다.");
      return;
    }

    setAddrText("위치를 찾는 중입니다...");

    navigator.geolocation.getCurrentPosition(
      function (pos) {
        myLat = pos.coords.latitude;
        myLng = pos.coords.longitude;
        baseLat = myLat; baseLng = myLng;

        if (!map) initMap(myLat, myLng);
        centerTo(myLat, myLng, 4);
        coordToAddr(myLat, myLng);

        // ✅ 내 위치 버튼도 반경 표시
        drawRadius(myLat, myLng, 1.0);

        loadFleaPins({ lat: myLat, lng: myLng, rkm: 1.0 });
      },
      
      function (err) {
        if (err && err.code === 1) setAddrText("위치 권한을 허용해 주세요.");
        else if (err && err.code === 2) setAddrText("위치를 가져올 수 없어요(신호/기기 확인).");
        else if (err && err.code === 3) setAddrText("위치 요청 시간이 초과됐어요. 다시 눌러 주세요.");
        else setAddrText("위치를 가져오지 못했어요.");
        // ✅ 위치를 못 받아도 핀은 보여주기(전체 요청)
        loadFleaPins({ lat: null, lng: null, rkm: null });
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  }

  function renderResults(list) {
    if (!elResult) return;
    elResult.innerHTML = "";

    if (!list || !list.length) {
      elResult.innerHTML = `
        <div class="lm-item">
          <div class="lm-pin">!</div>
          <div class="lm-meta">
            <p class="lm-name">검색 결과가 없어요.</p>
            <div class="lm-addr">다른 키워드로 검색해 보세요.</div>
          </div>
        </div>
      `;
      return;
    }

    list.forEach((place, idx) => {
      const div = document.createElement("div");
      div.className = "lm-item";

      const name = place.place_name || "";
      const addr = place.road_address_name || place.address_name || "";

      div.innerHTML = `
        <div class="lm-pin">${idx + 1}</div>
        <div class="lm-meta">
          <p class="lm-name">${name}</p>
          <div class="lm-addr">${addr}</div>
        </div>
      `;

      div.addEventListener("click", () => {
        const lat = Number(place.y);
        const lng = Number(place.x);
        centerTo(lat, lng, 4);
      });

      elResult.appendChild(div);
    });
  }

  function showPlaceOverlay(place) {
    closeOverlay();

    const lat = Number(place.y);
    const lng = Number(place.x);
    const pos = new kakao.maps.LatLng(lat, lng);

    const addr = place.road_address_name || place.address_name || "";
    const title = place.place_name || "";

    const writeUrl =
      "/board/flea/write/?" +
      "addr=" +
      encodeURIComponent(`${title}${addr ? " · " + addr : ""}`) +
      "&lat=" +
      encodeURIComponent(lat.toFixed(6)) +
      "&lng=" +
      encodeURIComponent(lng.toFixed(6));

    const content = `
      <div style="
        background:#fff; border-radius:12px; padding:10px 12px;
        box-shadow:0 10px 25px rgba(0,0,0,12);
        font-size:13px; line-height:1.35; min-width:230px;">
        <div style="font-weight:900; margin-bottom:6px;">${title}</div>
        <div style="color:#777; font-size:12px;">${addr}</div>

        <div style="display:flex; gap:8px; margin-top:10px;">
          <a href="${writeUrl}"
            style="flex:1; text-align:center; text-decoration:none;
              border:0; border-radius:10px; padding:9px 10px;
              background:#ff6b6b; color:#fff; font-weight:900;">
            여기로 글쓰기
          </a>

          <button id="lm_close_overlay"
            style="border:1px solid #eee; border-radius:10px;
              padding:9px 10px; background:#fff; font-weight:900; cursor:pointer;">
            닫기
          </button>
        </div>
      </div>
    `;

    overlay = new kakao.maps.CustomOverlay({
      position: pos,
      content: content,
      yAnchor: 1.28,
      zIndex: 9999,
    });

    overlay.setMap(map);

    setTimeout(() => {
      if (map) panToWithOffset(lat, lng, 70);
      const btn = document.getElementById("lm_close_overlay");
      if (btn) btn.onclick = closeOverlay;
    }, 0);
  }

  function showFleaOverlay(item, lat, lng) {
    closeOverlay();

    const pos = new kakao.maps.LatLng(lat, lng);
    const title = item.title || "";
    const detailUrl = item.url || "#";
    const id = item.id;

    // ✅ 썸네일/가격/거리
    const imgUrl = item.img || "";
    const priceText = formatPriceKRW(item.price);

    let distValue = "";
    if (Number.isFinite(baseLat) && Number.isFinite(baseLng)) {
      const km = distanceKm(baseLat, baseLng, Number(lat), Number(lng));
      const d = formatDistanceKm(km);
      if (d) distValue = d;
    }

    // ✅ (요청) 두 핀 + 점선 아이콘(이미지 파일 추가 없이 사용 가능: SVG data URI)
    const routeIcon = "data:image/svg+xml;utf8," + encodeURIComponent(`
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 64 64">
        <path d="M18 28c-7.2 0-13-5.8-13-13S10.8 2 18 2s13 5.8 13 13-5.8 13-13 13zm0-20a7 7 0 1 0 0 14 7 7 0 0 0 0-14z" fill="#495057"/>
        <path d="M18 28c-5 7-10 14-10 20 0 6.6 4.9 12 10 12s10-5.4 10-12c0-6-5-13-10-20z" fill="#495057"/>
        <path d="M46 34c-6.1 0-11-4.9-11-11s4.9-11 11-11 11 4.9 11 11-4.9 11-11 11zm0-16a5 5 0 1 0 0 10 5 5 0 0 0 0-10z" fill="#495057"/>
        <path d="M46 34c-4.2 6-8.5 11.5-8.5 16.5 0 5.6 4 10 8.5 10s8.5-4.4 8.5-10c0-5-4.3-10.5-8.5-16.5z" fill="#495057"/>
        <path d="M24 40c6 0 10-8 16-8" fill="none" stroke="#adb5bd" stroke-width="4" stroke-linecap="round" stroke-dasharray="4 7"/>
      </svg>
    `);

    // ✅ 모달 팝업 생성
    openFleaModal({
      title,
      imgUrl,
      price: priceText,
      distance: distValue,
      detailUrl,
      postId: id,
      routeIcon
    });
  }

  // 플리마켓 상세 모달
  function openFleaModal(data) {
    const existingModal = document.getElementById("flea-detail-modal");
    if (existingModal) existingModal.remove();

    const modal = document.createElement("div");
    modal.id = "flea-detail-modal";
    modal.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.6);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10001;
      animation: fadeIn 0.2s ease;
    `;

    modal.innerHTML = `
      <style>
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      </style>
      <div style="
        background: #fff;
        border-radius: 12px;
        max-width: 280px;
        width: 80%;
        max-height: 80vh;
        overflow-y: auto;
        padding: 14px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        animation: slideUp 0.3s ease;
      ">
        <!-- 제목과 닫기 버튼 -->
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
          <h2 style="margin:0; font-size:15px; font-weight:900; color:#212529; line-height:1.3; word-break:break-word; flex:1; padding-right:8px;">
            ${data.title}
          </h2>
          <button style="
            min-width:24px; height:24px;
            border:none;
            background:#f1f3f5;
            border-radius:50%;
            font-size:16px;
            cursor:pointer;
            display:flex;
            align-items:center;
            justify-content:center;
            transition: background 0.2s;
            flex-shrink: 0;
          " 
          onmouseover="this.style.background='#e9ecef'"
          onmouseout="this.style.background='#f1f3f5'"
          onclick="document.getElementById('flea-detail-modal').remove();">×</button>
        </div>

        <!-- 이미지 -->
        ${data.imgUrl ? `
          <div style="
            width:100%;
            height:150px;
            border-radius:8px;
            overflow:hidden;
            margin-bottom:12px;
            background:#f1f3f5;
          ">
            <img src="${data.imgUrl}" alt="" style="width:100%; height:100%; object-fit:cover;">
          </div>
        ` : `
          <div style="
            width:100%;
            height:150px;
            border-radius:8px;
            margin-bottom:12px;
            background:#f1f3f5;
            display:flex;
            align-items:center;
            justify-content:center;
            color:#adb5bd;
            font-weight:900;
            font-size:12px;
          ">이미지 없음</div>
        `}

        <!-- 가격과 거리 정보 -->
        <div style="
          border:1px solid #eee;
          border-radius:8px;
          padding:10px;
          background:#fafafa;
          margin-bottom:12px;
        ">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="color:#868e96; font-weight:900; font-size:11px;">가격</span>
            <span style="color:#ff6b6b; font-weight:900; font-size:14px;">${data.price || "가격 미정"}</span>
          </div>
          
          ${data.distance ? `
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="display:flex; align-items:center; gap:4px;">
              <img src="${data.routeIcon}" alt="" style="width:12px; height:12px; display:block;">
              <span style="color:#868e96; font-weight:900; font-size:11px;">거리</span>
            </div>
            <span style="color:#495057; font-weight:900; font-size:14px;">${data.distance}</span>
          </div>
          ` : ''}
        </div>

        <!-- 버튼 -->
        <div style="display:flex; gap:6px;">
          <a href="${data.detailUrl}" style="
            flex:1;
            display:flex;
            align-items:center;
            justify-content:center;
            padding:9px;
            background:#ff6b6b;
            color:#fff;
            font-weight:900;
            font-size:13px;
            border-radius:7px;
            border:none;
            text-decoration:none;
            cursor:pointer;
            transition: background 0.2s;
          " 
          onmouseover="this.style.background='#ff5252'"
          onmouseout="this.style.background='#ff6b6b'">
            게시글 이동
          </a>
          
          <button style="
            min-width:60px;
            padding:9px;
            background:#fff;
            color:#495057;
            font-weight:900;
            font-size:13px;
            border-radius:7px;
            border:1px solid #dee2e6;
            cursor:pointer;
            transition: all 0.2s;
          "
          onmouseover="this.style.background='#f8f9fa'"
          onmouseout="this.style.background='#fff'"
          onclick="document.getElementById('flea-detail-modal').remove();">
            닫기
          </button>
        </div>
      </div>
    `;

    // 지도 컨테이너에 추가
    elMap.appendChild(modal);
    
    // 배경 클릭 시 닫기
    modal.onclick = (e) => {
      if (e.target === modal) modal.remove();
    };
  }



  function doKeywordSearch(query) {
    if (!ps || !map) return;
    clearMarkers();
    closeOverlay();

    const center = getSearchCenter();

    ps.keywordSearch(
      query,
      function (data, status) {
        if (status !== kakao.maps.services.Status.OK) {
          renderResults([]);
          return;
        }

        renderResults(data);

        data.forEach((place) => {
          const lat = Number(place.y);
          const lng = Number(place.x);

          const marker = new kakao.maps.Marker({
            map,
            position: new kakao.maps.LatLng(lat, lng),
          });

          markers.push(marker);

          kakao.maps.event.addListener(marker, "click", function () {
            showPlaceOverlay(place);
          });
        });

        if (data[0]) {
          centerTo(Number(data[0].y), Number(data[0].x), 4);
        }
      },
      { location: new kakao.maps.LatLng(center.lat, center.lng) }
    );
  }

  function drawRadiusFromQuery() {
    const p = new URLSearchParams(location.search);
    const clat = p.get("clat");
    const clng = p.get("clng");
    const r = p.get("r");

    if (clat && clng) {
      const lat = Number(clat);
      const lng = Number(clng);
      const rkm = Number(r || 1);

      if (Number.isFinite(lat) && Number.isFinite(lng)) {
        centerTo(lat, lng, 4);
        drawRadius(lat, lng, rkm);
      }
    } else {
      clearRadius();
    }
  }

  if (btnSearch) {
    btnSearch.addEventListener("click", function () {
      const q = (elKeyword && elKeyword.value ? elKeyword.value : "").trim();
      if (!q) return;
      doKeywordSearch(q);
    });
  }

  if (btnMyLoc) {
    btnMyLoc.addEventListener("click", function () {
      closeOverlay();
      findMyLocation();
    });
  }

  const btnMyAddr = $("lm_btn_myaddr");
  if (btnMyAddr) {
    btnMyAddr.addEventListener("click", function () {
      closeOverlay();
      const addr = (CFG.defaultAddress || "").trim();
      
      setCenterFromUserAddress(
        (lat, lng) => {
          drawRadius(lat, lng, 1.0);
          loadFleaPins({ lat, lng, rkm: 1.0 });
        },
        () => {
          // 주소가 있으면 표시, 없으면 안내 메시지
          if (addr) {
            setAddrText(`회원 주소: ${addr}`);
          } else {
            setAddrText("회원 주소를 찾지 못했어요. (마이페이지 주소 저장/정확도 확인)");
          }
        }
      );
    });
  }

  quickBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const q = this.getAttribute("data-q") || "";
      if (!q) return;
      if (elKeyword) elKeyword.value = q;
      doKeywordSearch(q);
    });
  });

  if (window.kakao && kakao.maps && kakao.maps.load) {
    kakao.maps.load(function () {
      initMap(37.5665, 126.9780);

      setCenterFromUserAddress(
        (lat, lng) => {
          drawRadius(lat, lng, 1.0);
          loadFleaPins({ lat, lng, rkm: 1.0 });
          drawRadiusFromQuery();
        },
        () => {
          findMyLocation();
          drawRadiusFromQuery();
        }
      );
    });
  }
})();
