// /static/js/flea_location_picker.js
// Flea 글쓰기에서 거래 위치 선택 -> hidden input(location_address/latitude/longitude)에 저장

(function () {
  const $ = (id) => document.getElementById(id);

  const mapEl = $("lm_pick_map");
  if (!mapEl) return;

  const keywordEl = $("lm_pick_keyword");
  const btnSearch = $("lm_pick_search");
  const btnMyLoc = $("lm_pick_myloc");
  const btnClear = $("lm_pick_clear");
  const resultEl = $("lm_pick_result");
  const pickedText = $("lm_picked_text");

  // Django form hidden inputs (id는 Django가 자동으로 id_location_address 이런 식으로 줌)
  const inAddr = $("id_location_address");
  const inLat = $("id_latitude");
  const inLng = $("id_longitude");

  let map = null;
  let ps = null;
  let markers = [];
  let overlay = null;
  let pickedMarker = null; // ✅ 선택된 위치(1개 고정) 마커


  function clearMarkers() {
    markers.forEach((m) => m.setMap(null));
    markers = [];
  }
  function closeOverlay() {
    if (overlay) {
      overlay.setMap(null);
      overlay = null;
    }
  }

  function setPicked(addr, lat, lng) {
    if (inAddr) inAddr.value = addr || "";
    if (inLat) inLat.value = lat || "";
    if (inLng) inLng.value = lng || "";

    // ✅ 지도에 선택 위치 마커 표시(1개 고정)
    if (map && lat && lng) {
        const pos = new kakao.maps.LatLng(Number(lat), Number(lng));

        if (!pickedMarker) {
        pickedMarker = new kakao.maps.Marker({ map, position: pos });
        } else {
        pickedMarker.setPosition(pos);
        pickedMarker.setMap(map);
        }

        // 사용자가 확인하기 쉽게 선택 위치로 살짝 이동
        map.panTo(pos);
    }

    // ✅ 위치 제거(빈 값)일 때는 마커도 제거
    if (map && (!lat || !lng)) {
        if (pickedMarker) pickedMarker.setMap(null);
    }


    if (pickedText) {
      if (!addr) pickedText.textContent = "아직 선택된 위치가 없어요. (지도 마커를 클릭하면 저장돼요)";
      else pickedText.textContent = `${addr}  (lat:${lat}, lng:${lng})`;
    }
  }

  function initMap(lat, lng) {
    const center = new kakao.maps.LatLng(lat, lng);
    map = new kakao.maps.Map(mapEl, { center, level: 4 });
    ps = new kakao.maps.services.Places();
  }

  function myLocation() {
    if (!navigator.geolocation) {
      if (!map) initMap(37.5665, 126.9780);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        if (!map) initMap(lat, lng);
        map.panTo(new kakao.maps.LatLng(lat, lng));
      },
      () => {
        if (!map) initMap(37.5665, 126.9780);
      }
    );
  }

  function showOverlay(place) {
    closeOverlay();
    const lat = Number(place.y);
    const lng = Number(place.x);
    const pos = new kakao.maps.LatLng(lat, lng);

    const addr = place.road_address_name || place.address_name || "";
    const content = `
      <div style="background:#fff;border-radius:12px;padding:10px 12px;
                  box-shadow:0 10px 25px rgba(0,0,0,.12);font-size:13px;min-width:200px;">
        <div style="font-weight:900;margin-bottom:6px;">${place.place_name}</div>
        <div style="color:#777;font-size:12px;">${addr}</div>
        <div style="margin-top:8px;">
          <button id="lm_pick_apply_btn" style="border:0;border-radius:10px;padding:8px 10px;
                  background:#ff6b6b;color:#fff;font-weight:900;cursor:pointer;">이 위치로 저장</button>
        </div>
      </div>
    `;

    overlay = new kakao.maps.CustomOverlay({
      position: pos,
      content,
      yAnchor: 1.2,
      zIndex: 5,
    });
    overlay.setMap(map);

    // overlay 내부 버튼 이벤트는 DOM이 생긴 다음에 잡아야 함
    setTimeout(() => {
      const applyBtn = document.getElementById("lm_pick_apply_btn");
      if (applyBtn) {
        applyBtn.onclick = () => {
          // 저장할 주소는 place_name + addr 형태가 보기 좋음
          const saveAddr = `${place.place_name}${addr ? " · " + addr : ""}`;
          setPicked(saveAddr, lat.toFixed(6), lng.toFixed(6));
          closeOverlay();
        };
      }
    }, 0);
  }

  function renderResults(list) {
    if (!resultEl) return;
    resultEl.innerHTML = "";

    list.forEach((place) => {
      const addr = place.road_address_name || place.address_name || "";
      const div = document.createElement("div");
      div.className = "lm-pick-item";
      div.innerHTML = `
        <div class="name">${place.place_name}</div>
        <div class="addr">${addr}</div>
      `;
      div.onclick = () => {
        const lat = Number(place.y);
        const lng = Number(place.x);
        map.panTo(new kakao.maps.LatLng(lat, lng));
      };
      resultEl.appendChild(div);
    });
  }

  function searchPlaces() {
    const keyword = (keywordEl?.value || "").trim();
    if (!keyword || !ps || !map) return;

    ps.keywordSearch(keyword, (data, status) => {
      if (status !== kakao.maps.services.Status.OK || !data.length) {
        if (resultEl) resultEl.innerHTML = `<div class="lm-pick-item"><div class="name">검색 결과가 없어요.</div></div>`;
        clearMarkers();
        closeOverlay();
        return;
      }

      clearMarkers();
      closeOverlay();

      const bounds = new kakao.maps.LatLngBounds();
      data.forEach((place) => {
        const lat = Number(place.y);
        const lng = Number(place.x);
        const pos = new kakao.maps.LatLng(lat, lng);

        const marker = new kakao.maps.Marker({ map, position: pos });
        markers.push(marker);
        bounds.extend(pos);

        kakao.maps.event.addListener(marker, "click", () => showOverlay(place));
      });

      map.setBounds(bounds);
      renderResults(data);
    });
  }

  btnMyLoc?.addEventListener("click", myLocation);
  btnSearch?.addEventListener("click", searchPlaces);
  keywordEl?.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      searchPlaces();
    }
  });

  btnClear?.addEventListener("click", () => setPicked("", "", ""));

  kakao.maps.load(() => {
    // ✅ 목록 지도에서 넘어온 값 자동 채움 (?addr=...&lat=...&lng=...)
    const params = new URLSearchParams(window.location.search);
    const qAddr = params.get("addr");
    const qLat = params.get("lat");
    const qLng = params.get("lng");

    if (qLat && qLng) {
        const lat = Number(qLat);
        const lng = Number(qLng);

        initMap(lat, lng);                 // 지도 중심을 전달받은 위치로
        setPicked(qAddr || "", lat.toFixed(6), lng.toFixed(6));  // hidden input 자동 채움
        return; // ✅ 여기서 끝! (내 위치로 초기화하지 않음)
    }

    // 수정 화면이면 기존 값이 있을 수 있음 -> 지도 중심만 잡아줌
    const lat = inLat?.value ? Number(inLat.value) : null;
    const lng = inLng?.value ? Number(inLng.value) : null;

    if (lat && lng) {
      initMap(lat, lng);
      setPicked(inAddr?.value || "", lat.toFixed(6), lng.toFixed(6));
    } else {
      myLocation();
      setPicked("", "", "");
    }
  });
})();
