// static/js/banner-slider.js
(function () {
  function initBanner2() {
    const track = document.querySelector(".banner2-track");
    const items = document.querySelectorAll(".banner2-item");
    const prevBtn = document.querySelector(".banner2-nav.prev");
    const nextBtn = document.querySelector(".banner2-nav.next");

    if (!track || items.length === 0 || !prevBtn || !nextBtn) {
      console.warn("[banner2] 요소 없음", {
        track: !!track,
        items: items.length,
        prevBtn: !!prevBtn,
        nextBtn: !!nextBtn,
      });
      return;
    }

    // ✅ 중복 초기화 방지
    if (track.dataset.inited === "1") {
      console.log("[banner2] already inited");
      return;
    }
    track.dataset.inited = "1";

    // ✅ 혹시 flex/transition이 다른 CSS에 의해 깨졌을 때 대비
    track.style.display = "flex";
    track.style.willChange = "transform";
    if (!track.style.transition) track.style.transition = "transform 0.45s ease";

    let index = 0;
    const total = items.length;

    function update() {
      const value = `translateX(-${index * 100}%)`;
      track.style.transform = value;
      console.log("[banner2] update =>", index, value);
    }

    function moveNext() {
      index = (index + 1) % total;
      update();
    }

    function movePrev() {
      index = (index - 1 + total) % total;
      update();
    }

    nextBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log("[banner2] next click");
      moveNext();
    });

    prevBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log("[banner2] prev click");
      movePrev();
    });

    update();

    // 자동재생 (원하면 삭제)
    setInterval(moveNext, 5000);

    console.log("[banner2] init done. total =", total);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initBanner2);
  } else {
    initBanner2();
  }
})();
