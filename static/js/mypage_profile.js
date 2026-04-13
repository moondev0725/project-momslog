/* =========================
   mypage_profile.js (통째 복붙용)
   - 이메일 인증: 기존 로직 유지(잠금/숨김 포함)
   - 닉네임 UX: 확인중/성공/실패 + input 테두리 상태 + 저장시 강제 검증
   - submit 검증: 한 번만(중복 바인딩 제거)
========================= */

const CFG = window.MYPAGE_PROFILE_CONFIG || {};
const $ = (id) => document.getElementById(id);

/* -------------------------
   상태
-------------------------- */
let nicknameTimer = null;
let lastNick = "";
let nickAvailable = false;
let nickChecked = false;

let emailVerified = false;
let lastVerifiedEmail = "";

/* -------------------------
   메시지(회색/초록/빨강)
-------------------------- */
function setMsg(elId, text, type) {
  const el = $(elId);
  if (!el) return;
  el.textContent = text || "";
  el.style.color =
    type === "ok" ? "green" :
    type === "bad" ? "red" :
    "#777"; // muted
}

/* -------------------------
   공통: 입력 상태 클래스(테두리 UX)
-------------------------- */
function setInputState(inputId, state) {
  const el = $(inputId);
  if (!el) return;
  el.classList.remove("is-ok", "is-bad", "is-wait");
  if (state === "ok") el.classList.add("is-ok");
  if (state === "bad") el.classList.add("is-bad");
  if (state === "wait") el.classList.add("is-wait");
}

function getInitialNickname() {
  // profile.html에서 data-initial을 안 달았어도 CFG.initialNickname으로 동작
  const el = $("nickname");
  return ((el?.dataset?.initial || CFG.initialNickname) || "").trim();
}

/* -------------------------
   이메일 인증 UI
-------------------------- */
function showEmailVerifyArea(show) {
  const area = $("emailVerifyArea");
  if (!area) return;
  area.classList.toggle("is-hidden", !show);
}

/* ✅ 이메일 인증 완료 후 UI 잠금/해제(버튼 숨김 포함) */
function lockEmailUI(locked) {
  const emailEl = $("email");
  const sendBtn = $("emailSendBtn");
  const verifyBtn = $("emailVerifyBtn");
  const codeInput = $("emailCode");

  if (emailEl) emailEl.readOnly = !!locked;

  if (sendBtn) {
    sendBtn.classList.toggle("is-hidden", !!locked);
    if (!locked) sendBtn.textContent = "인증번호 발송";
  }

  if (verifyBtn) {
    verifyBtn.classList.toggle("is-hidden", !!locked);
    verifyBtn.disabled = false;
  }

  if (codeInput) codeInput.readOnly = false;

  if (locked) showEmailVerifyArea(false);
}

function resetEmailVerifyState() {
  emailVerified = false;
  lastVerifiedEmail = "";

  if ($("emailCode")) $("emailCode").value = "";
  if ($("emailVerifyBtn")) $("emailVerifyBtn").disabled = false;
  if ($("emailCode")) $("emailCode").readOnly = false;

  lockEmailUI(false);
}

/* -------------------------
   닉네임 실시간 중복확인 (UX 업그레이드)
-------------------------- */
function setNickMsg(text, type) {
  setMsg("nicknameMsg", text, type);
}

async function checkNicknameAuto() {
  nicknameTimer = null;

  const nickname = ($("nickname")?.value || "").trim();
  const initialNick = getInitialNickname();

  if (!nickname) {
    nickAvailable = false;
    nickChecked = false;
    setInputState("nickname", "");
    setNickMsg("", "muted");
    return;
  }

  // 기존 닉네임이면 체크 완료로 간주
  if (nickname === initialNick) {
    nickAvailable = true;
    nickChecked = true;
    setInputState("nickname", "ok");
    setNickMsg("현재 등록된 닉네임입니다.", "muted");
    return;
  }

  // 같은 값 재검사 방지
  if (nickname === lastNick) return;
  lastNick = nickname;

  // 확인중
  nickAvailable = false;
  nickChecked = false;
  setInputState("nickname", "wait");
  setNickMsg("확인 중...", "muted");

  try {
    const url = `${CFG.checkNicknameUrl}?nickname=${encodeURIComponent(nickname)}`;
    const res = await fetch(url);
    const data = await res.json();

    if (!data.ok) {
      nickAvailable = false;
      nickChecked = false;
      setInputState("nickname", "bad");
      setNickMsg("중복확인 중 오류가 발생했습니다.", "bad");
      return;
    }

    nickAvailable = !!data.available;
    nickChecked = true;

    if (nickAvailable) {
      setInputState("nickname", "ok");
      setNickMsg(data.msg || "사용 가능한 닉네임입니다.", "ok");
    } else {
      setInputState("nickname", "bad");
      setNickMsg(data.msg || "이미 사용 중인 닉네임입니다.", "bad");
    }
  } catch {
    nickAvailable = false;
    nickChecked = false;
    setInputState("nickname", "bad");
    setNickMsg("중복확인 중 오류가 발생했습니다.", "bad");
  }
}

function onNicknameInput() {
  const nickname = ($("nickname")?.value || "").trim();
  const initialNick = getInitialNickname();

  // 입력 시작하면 상태 초기화
  nickAvailable = false;
  nickChecked = false;
  setInputState("nickname", "");
  setNickMsg("", "muted");

  // 기존 닉이면 즉시 OK
  if (nickname && nickname === initialNick) {
    nickAvailable = true;
    nickChecked = true;
    setInputState("nickname", "ok");
    setNickMsg("현재 등록된 닉네임입니다.", "muted");
    return;
  }

  // 빈값이면 여기서 종료
  if (!nickname) return;

  if (nicknameTimer) clearTimeout(nicknameTimer);
  nicknameTimer = setTimeout(checkNicknameAuto, 500);
}

/* 저장 전: 닉네임 체크 강제 */
function validateNicknameBeforeSubmit(e) {
  const el = $("nickname");
  if (!el) return true;

  const nickname = (el.value || "").trim();
  const initialNick = getInitialNickname();

  if (!nickname) {
    e.preventDefault();
    nickAvailable = false;
    nickChecked = false;
    setInputState("nickname", "bad");
    setNickMsg("닉네임을 입력해 주세요.", "bad");
    el.focus();
    return false;
  }

  if (nickname === initialNick) {
    // 기존 닉네임이면 통과
    return true;
  }

  if (!nickChecked || !nickAvailable) {
    e.preventDefault();
    setInputState("nickname", "bad");
    setNickMsg("닉네임 중복확인을 통과해야 저장할 수 있습니다.", "bad");
    el.focus();
    return false;
  }

  return true;
}

/* -------------------------
   이메일 변경 인증
-------------------------- */
function isValidEmail(email) {
  const v = (email || "").trim();
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);
}

function setEmailMsg(text, type) {
  setMsg("emailMsg", text, type);
}

async function postForm(url, payload) {
  const csrftoken = document.querySelector("input[name=csrfmiddlewaretoken]")?.value;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "X-CSRFToken": csrftoken || "",
    },
    body: new URLSearchParams(payload),
  });
  return res.json();
}

/* ✅ 이메일 입력 상태에 따라 UI 싱크 */
function syncEmailUI() {
  const emailEl = $("email");
  const email = (emailEl?.value || "").trim();
  const initialEmail = (CFG.initialEmail || "").trim();
  const sendBtn = $("emailSendBtn");

  // 이메일을 건드리는 순간: 다시 인증 시작
  resetEmailVerifyState();
  showEmailVerifyArea(false);

  if (!sendBtn) return;

  if (!email) {
    sendBtn.disabled = true;
    setEmailMsg("이메일을 입력해 주세요.", "bad");
    return;
  }

  if (!isValidEmail(email)) {
    sendBtn.disabled = true;
    setEmailMsg("이메일 형식이 올바르지 않습니다.", "bad");
    return;
  }

  if (email === initialEmail) {
    sendBtn.disabled = true;
    setEmailMsg("현재 등록된 이메일입니다.", "muted");
    return;
  }

  sendBtn.disabled = false;
  setEmailMsg("이메일 변경 시 인증이 필요합니다.", "muted");
}

async function sendEmailCode() {
  const email = ($("email")?.value || "").trim();
  const initialEmail = (CFG.initialEmail || "").trim();

  if (!email) return setEmailMsg("이메일을 입력해 주세요.", "bad");
  if (!isValidEmail(email)) return setEmailMsg("이메일 형식이 올바르지 않습니다.", "bad");
  if (email === initialEmail) return;

  resetEmailVerifyState();

  const data = await postForm(CFG.sendEmailCodeUrl, { email });

  if (data.ok && data.same) {
    setEmailMsg("현재 등록된 이메일입니다.", "muted");
    showEmailVerifyArea(false);
    return;
  }

  if (!data.ok) {
    setEmailMsg(data.error || "메일 발송에 실패했습니다.", "bad");
    showEmailVerifyArea(false);
    return;
  }

  setEmailMsg("인증번호를 발송했습니다. 메일을 확인해 주세요.", "ok");
  showEmailVerifyArea(true);
  $("emailCode")?.focus();
}

async function verifyEmailCode() {
  const email = ($("email")?.value || "").trim();
  const code = ($("emailCode")?.value || "").trim();

  if (!email) return setEmailMsg("이메일을 입력해 주세요.", "bad");
  if (!code) return setEmailMsg("인증번호를 입력해 주세요.", "bad");

  const data = await postForm(CFG.verifyEmailCodeUrl, { email, code });

  if (!data.ok) {
    resetEmailVerifyState();
    setEmailMsg(data.error || "인증에 실패했습니다.", "bad");
    return;
  }

  emailVerified = true;
  lastVerifiedEmail = email;

  setEmailMsg("이메일 인증이 완료되었습니다.", "ok");
  lockEmailUI(true);
}

/* -------------------------
   주소 검색 (Daum Postcode)
-------------------------- */
function openAddressSearch() {
  if (!window.daum || !window.daum.Postcode) {
    alert("주소 검색 모듈을 불러오지 못했습니다.\n새로고침(Ctrl+Shift+R) 후 다시 시도해 주세요.");
    return;
  }

  new window.daum.Postcode({
    oncomplete: function (data) {
      const baseAddr = (data.roadAddress || data.jibunAddress || "").trim();

      const addressEl = $("address");
      if (addressEl) addressEl.value = baseAddr;

      const detailEl = $("addressDetail");
      if (detailEl) {
        detailEl.value = "";
        detailEl.focus();
      }
    }
  }).open();
}

/* -------------------------
   저장 전 최소 체크 (한 번만)
-------------------------- */
function onSubmit(e) {
  const email = ($("email")?.value || "").trim();
  const initialEmail = (CFG.initialEmail || "").trim();

  // 닉네임 검증(UX + 강제)
  if (!validateNicknameBeforeSubmit(e)) return;

  // 이메일 변경이면 인증 완료 필수
  if (email !== initialEmail) {
    if (!emailVerified || lastVerifiedEmail !== email) {
      e.preventDefault();
      setEmailMsg("이메일 변경은 인증 완료 후 저장할 수 있습니다.", "bad");
      $("email")?.focus();
      return;
    }
  }
}

/* -------------------------
   바인딩
-------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  // 닉네임
  $("nickname")?.addEventListener("input", onNicknameInput);

  // 이메일
  $("email")?.addEventListener("input", syncEmailUI);
  $("emailSendBtn")?.addEventListener("click", sendEmailCode);
  $("emailVerifyBtn")?.addEventListener("click", verifyEmailCode);

  // 주소
  $("addrSearchBtn")?.addEventListener("click", openAddressSearch);

  // 저장 (submit 리스너는 한 번만)
  $("profileForm")?.addEventListener("submit", onSubmit);

  // 초기 상태
  setNickMsg("현재 등록된 닉네임입니다.", "muted");
  setInputState("nickname", "ok");
  syncEmailUI();
});
