document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("mindModal");
  if (!modal) return;

  const viewQuestions = document.getElementById("mindViewQuestions");
  const viewResult = document.getElementById("mindViewResult");
  const footerQuestions = document.getElementById("mindFooterQuestions");
  const footerResult = document.getElementById("mindFooterResult");
  const goBtn = document.getElementById("mindGoBtn");
  const backBtn = document.getElementById("mindBackBtn");
  const questions = Array.from(modal.querySelectorAll(".mind-q[data-q]"));

  const elEmoji = document.getElementById("mindResultEmoji");
  const elLevelText = document.getElementById("mindResultLevelText");
  const elSub = document.getElementById("mindResultSub");
  const elMsg = document.getElementById("mindResultMsg");
  const elScore = document.getElementById("mindResultScore");
  const elMax = document.getElementById("mindResultMax");
  const elFill = document.getElementById("mindResultBarFill");

  function applyMoodTheme(levelText) {
    let mood = "stable";
    if (levelText === "매우 불안") mood = "very-anxious";
    else if (levelText === "약간 불안") mood = "anxious";
    else if (levelText === "안정") mood = "stable";
    else if (levelText === "약간 행복") mood = "happy";
    else if (levelText === "매우 행복") mood = "very-happy";
    modal.setAttribute("data-mood", mood);
  }

  function selectScore(qEl, chosenBtn) {
    qEl.querySelectorAll(".mind-score").forEach((btn) => {
      const isChosen = btn === chosenBtn;
      btn.setAttribute("aria-pressed", isChosen ? "true" : "false");
      btn.classList.toggle("is-selected", isChosen);
    });
  }

  modal.addEventListener("click", (e) => {
    const btn = e.target.closest(".mind-score");
    if (!btn) return;
    const qEl = btn.closest(".mind-q[data-q]");
    if (!qEl) return;
    selectScore(qEl, btn);
  });

  function getSelectedScores() {
    const scores = [];
    for (const qEl of questions) {
      const chosen = qEl.querySelector('.mind-score[aria-pressed="true"]');
      if (!chosen) return null;
      scores.push(parseInt(chosen.dataset.score, 10));
    }
    return scores;
  }

  function calcLevel(scores) {
    const sum = scores.reduce((a, b) => a + b, 0);
    const avg = sum / scores.length;
    let levelText = "안정";
    if (avg < 1.8) levelText = "매우 불안";
    else if (avg < 2.6) levelText = "약간 불안";
    else if (avg < 3.4) levelText = "안정";
    else if (avg < 4.2) levelText = "약간 행복";
    else levelText = "매우 행복";
    let levelNum = 3;
    if (avg < 1.8) levelNum = 1;
    else if (avg < 2.6) levelNum = 2;
    else if (avg < 3.4) levelNum = 3;
    else if (avg < 4.2) levelNum = 4;
    else levelNum = 5;
    return { sum, avg, levelText, levelNum };
  }

  function levelMeta(levelNum) {
    const map = {
      1: { emoji: "😔", sub: "지금은 정말 많이 버거운 상태예요.", msg: "하루 종일 참고 버티느라 힘들었죠? 혼자 감당하려 하지 않아도 괜찮아요. 비슷한 마음을 겪은 엄마들의 이야기를 먼저 읽어보세요. 말하지 않아도 위로가 될 수 있어요." },
      2: { emoji: "😕", sub: "조금씩 지치고 여유가 부족했을 수 있어요.", msg: "혹시 쉬고싶지 않나요? 지금 느끼는 감정을 짧게라도 꺼내놓으면 생각보다 가벼워질 수 있어요. 공감받는 글 하나만 읽어보세요." },
      3: { emoji: "😐", sub: "크게 흔들리진 않았지만 피로는 쌓여 있어요.", msg: "문제는 없지만 계속 이렇게 버티기만 하면 어느 순간 힘들어질 수 있어요. 오늘 하루 중 가장 힘들었던 순간 하나만 떠올려보세요. 그걸 적는 것만으로도 정리가 시작돼요." },
      4: { emoji: "🙂", sub: "오늘 하루, 꽤 잘 버텨냈어요.", msg: "완벽하지 않아도 충분히 잘하고 있어요. 오늘 내가 해낸 일 한 가지를 스스로 인정해 주세요. 그리고 여유가 된다면 다른 엄마의 글에 공감 버튼 하나 눌러보세요." },
      5: { emoji: "😊", sub: "마음이 비교적 안정적인 좋은 상태예요.", msg: "지금의 이 기분을 오래 가져가고 싶지 않나요? 오늘의 좋은 흐름을 기록으로 남겨보세요. 당신의 이야기가 누군가에게 큰 위로가 될 수 있어요." },
    };
    return map[levelNum] || map[3];
  }

  function showResultView() {
    if (viewQuestions) viewQuestions.style.display = "none";
    if (viewResult) viewResult.style.display = "block";
    if (footerQuestions) footerQuestions.style.display = "none";
    if (footerResult) footerResult.style.display = "block";
    modal.classList.add("is-result");
  }

  function showQuestionsView() {
    if (viewResult) viewResult.style.display = "none";
    if (viewQuestions) viewQuestions.style.display = "block";
    if (footerResult) footerResult.style.display = "none";
    if (footerQuestions) footerQuestions.style.display = "flex";
    modal.classList.remove("is-result");
  }

  if (!goBtn) {
    console.warn("mindGoBtn(id='mindGoBtn')을 찾지 못함");
    return;
  }

  goBtn.addEventListener("click", () => {
    const scores = getSelectedScores();
    if (!scores) {
      alert("모든 문항을 선택해주세요!");
      return;
    }
    const { sum, levelText, levelNum } = calcLevel(scores);
    const meta = levelMeta(levelNum);
    applyMoodTheme(levelText);
    if (elLevelText) elLevelText.textContent = levelText;
    if (elEmoji) elEmoji.textContent = meta.emoji;
    if (elSub) elSub.textContent = meta.sub;
    if (elMsg) elMsg.textContent = meta.msg;
    const maxRawScore = scores.length * 5;
    const score100 = Math.round((sum / maxRawScore) * 100);
    if (elScore) elScore.textContent = String(score100);
    if (elMax) elMax.textContent = "100";
    if (elFill) elFill.style.width = `${score100}%`;
    showResultView();
  });

  if (backBtn) backBtn.addEventListener("click", showQuestionsView);
  showQuestionsView();
});
