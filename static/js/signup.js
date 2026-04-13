// ✅ 이메일 인증 상태 플래그 (전역)
let isEmailVerified = false;

/* ===============================
   공통 유틸
================================ */
const $ = (id) => document.getElementById(id);

const CFG = window.SIGNUP_CONFIG || {
  hasServerErrors: false,
  checkIdUrl: "/accounts/check-id/",
  checkNicknameUrl: "/accounts/check-nickname/",
  checkEmailUrl: "/accounts/check-email/",
  sendEmailCodeUrl: "/accounts/email/send-code/",
  verifyEmailCodeUrl: "/accounts/email/verify-code/",
};

function onlyNumber(el) {
  el.value = (el.value || "").replace(/\D/g, "");
}

function addOnceShake(el) {
  if (!el) return;
  el.classList.remove("shake");
  void el.offsetWidth;
  el.classList.add("shake");
  setTimeout(() => el.classList.remove("shake"), 250);
}

function setInputState(el, state) {
  if (!el) return;
  el.classList.remove("input-ok", "input-bad", "input-wait");
  if (state) el.classList.add(state);
}

/* ===============================
   ✅ 입력 유지(sessionStorage)
================================ */
const PERSIST_IDS = [
  "username",
  "real_name",
  "nickname",
  "email",
  "jumin1",
  "phone1",
  "phone2",
  "phone3",
  "address_main",
  "address_detail",
  "hidden_real_address",
  "emailCode",
];

function saveDraft() {
  PERSIST_IDS.forEach((id) => {
    const el = $(id);
    if (el) sessionStorage.setItem("signup_" + id, el.value || "");
  });

  // 성별
  const gender = document.querySelector('input[name="gender"]:checked')?.value || "";
  sessionStorage.setItem("signup_gender", gender);

  // 자녀 여부
  const hasChildren = $("has_children")?.value || "0";
  sessionStorage.setItem("signup_has_children", hasChildren);

  // 자녀 학령(복수)
  const checkedStages = Array.from(document.querySelectorAll('input[name="children_stages"]:checked'))
    .map((x) => x.value);
  sessionStorage.setItem("signup_children_stages", JSON.stringify(checkedStages));

  // 약관
  const terms = $("agree_terms")?.checked ? "1" : "0";
  sessionStorage.setItem("signup_terms", terms);

  // ✅ 이메일 인증 여부
  sessionStorage.setItem("signup_email_verified", isEmailVerified ? "1" : "0");
}

function clearDraft() {
  Object.keys(sessionStorage).forEach((k) => {
    if (k.startsWith("signup_")) sessionStorage.removeItem(k);
  });
}

/* ===============================
   주민번호 / 전화번호 / 주소 병합
================================ */
function mergeJumin() {
  const a = $("jumin1")?.value || "";
  const b = $("jumin2")?.value || "";
  const hidden = $("jumin");
  if (!hidden) return;

  if (a.length === 6 && b.length === 7) hidden.value = `${a}-${b}`;
  else hidden.value = a || b ? `${a}-${b}` : "";
}

function mergePhone() {
  const a = $("phone1")?.value || "";
  const b = $("phone2")?.value || "";
  const c = $("phone3")?.value || "";
  const hidden = $("phone");
  if (!hidden) return;

  if (a && b && c) hidden.value = `${a}-${b}-${c}`;
  else hidden.value = a || b || c ? `${a}-${b}-${c}` : "";
}

function mergeAddress() {
  const main = $("address_main")?.value || "";
  const detail = $("address_detail")?.value || "";
  const hidden = $("hidden_real_address");
  if (!hidden) return;

  hidden.value = (main + " " + detail).trim();
}

/* ===============================
   ✅ 이메일 인증 UI 헬퍼 (중복 제거 버전)
================================ */
function showEmailCodeWrap() {
  const wrap = $("emailCodeWrap");
  if (wrap) wrap.style.display = "block";
}

function hideEmailCodeWrap() {
  const wrap = $("emailCodeWrap");
  if (wrap) wrap.style.display = "none";
  const codeInput = $("emailCode");
  if (codeInput) codeInput.value = "";
}

function resetEmailVerifyState() {
  isEmailVerified = false;

  const checkMsg = $("email_check_msg");
  if (checkMsg) {
    checkMsg.textContent = "";
    checkMsg.style.color = "";
  }

  const statusEl = $("emailVerifyStatus");
  if (statusEl) {
    statusEl.textContent = "";
    statusEl.style.color = "";
  }

  const emailInput = $("email");
  const sendBtn = $("btnSendCode");

  if (emailInput) {
    emailInput.readOnly = false;
    emailInput.classList.remove("input-locked");
  }
  if (sendBtn) {
    sendBtn.disabled = false;
    sendBtn.classList.remove("btn-locked");
  }

  hideEmailCodeWrap();
  updateSubmitState();
}



function markEmailVerified() {
  isEmailVerified = true;

  // ✅ "사용 가능한 이메일입니다." 자리로 메시지 통일
  const checkMsg = $("email_check_msg");
  if (checkMsg) {
    checkMsg.textContent = "✅ 인증이 완료되었습니다.";
    checkMsg.style.color = "green";
  }

  // ✅ 아래 상태 영역은 비워두기(중복 방지)
  const statusEl = $("emailVerifyStatus");
  if (statusEl) {
    statusEl.textContent = "";
    statusEl.style.color = "";
  }

  const emailInput = $("email");
  const sendBtn = $("btnSendCode");

  if (emailInput) {
    emailInput.readOnly = true;
    emailInput.classList.add("input-locked");
    emailInput.blur(); // 포커스 빠지게
  }
  if (sendBtn) {
    sendBtn.disabled = true;
    sendBtn.classList.add("btn-locked");
  }

  hideEmailCodeWrap();
  updateSubmitState();
}




function restoreDraftIfServerErrors() {
  if (!CFG.hasServerErrors) {
    clearDraft();
    return;
  }

  PERSIST_IDS.forEach((id) => {
    const el = $(id);
    if (!el) return;
    if (!el.value) {
      const saved = sessionStorage.getItem("signup_" + id);
      if (saved !== null) el.value = saved;
    }
  });

  // 성별
  const g = sessionStorage.getItem("signup_gender");
  if (g) {
    const radio = document.querySelector(`input[name="gender"][value="${g}"]`);
    if (radio) radio.checked = true;
  }

  // 자녀 여부
  const hasChildren = sessionStorage.getItem("signup_has_children");
  if (hasChildren === "1" || hasChildren === "0") {
    if ($("has_children")) $("has_children").value = hasChildren;
    const ui = document.querySelector(`input[name="has_children_ui"][value="${hasChildren}"]`);
    if (ui) ui.checked = true;
    const box = $("childrenStageBox");
    if (box) box.style.display = hasChildren === "1" ? "block" : "none";
  }

  // 자녀 학령
  const stagesRaw = sessionStorage.getItem("signup_children_stages");
  try {
    const stages = JSON.parse(stagesRaw || "[]");
    document.querySelectorAll('input[name="children_stages"]').forEach((cb) => {
      cb.checked = stages.includes(cb.value);
    });
  } catch (_) {}

  // 약관
  const t = sessionStorage.getItem("signup_terms");
  if ($("agree_terms")) $("agree_terms").checked = t === "1";

  // ✅ 이메일 인증 여부
  const ev = sessionStorage.getItem("signup_email_verified");
  if (ev === "1") {
    // markEmailVerified가 메시지/잠금/상태를 한 번에 정리함
    markEmailVerified();
  }


  mergeJumin();
  mergePhone();
  mergeAddress();
}

/* ===============================
   비밀번호 보기 토글
================================ */
document.addEventListener("click", (e) => {
  const btn = e.target.closest(".toggle-eye");
  if (!btn) return;

  const targetId = btn.dataset.toggleTarget;
  const input = $(targetId);
  if (!input) return;

  const isPw = input.type === "password";
  input.type = isPw ? "text" : "password";
  btn.textContent = isPw ? "숨김" : "보기";
  input.focus();
});

/* ===============================
   Daum 주소 검색
================================ */
$("btnAddressSearch")?.addEventListener("click", () => {
  new daum.Postcode({
    oncomplete: function (data) {
      const addr = data.userSelectedType === "R" ? data.roadAddress : data.jibunAddress;
      $("address_main").value = addr;
      $("address_detail").focus();
      mergeAddress();
      updateSubmitState();
    },
  }).open();
});

/* ===============================
   비밀번호 규칙 & 안내
================================ */
function hasLetter(s) { return /[A-Za-z]/.test(s); }
function hasNumber(s) { return /\d/.test(s); }
function hasSpecial(s) { return /[^A-Za-z0-9]/.test(s); }

function isPasswordValid() {
  const pw = $("password1")?.value || "";
  const okLen = pw.length >= 8;
  const okMix = hasLetter(pw) && hasNumber(pw) && hasSpecial(pw);
  return okLen && okMix;
}

function updatePasswordRules() {
  const p1El = $("password1");
  const msg = $("pw_strength_msg");
  const pw = p1El?.value || "";

  const okLen = pw.length >= 8;
  const okMix = hasLetter(pw) && hasNumber(pw) && hasSpecial(pw);

  const elLen = $("pw_rule_len");
  const elMix = $("pw_rule_mix");

  if (elLen) elLen.style.color = okLen ? "green" : "red";
  if (elMix) elMix.style.color = okMix ? "green" : "red";

  if (!pw) {
    if (msg) msg.textContent = "";
    setInputState(p1El, null);
    return;
  }

  if (okLen && okMix) {
    if (msg) { msg.textContent = "좋아요! 조건을 만족하는 비밀번호예요."; msg.style.color = "green"; }
    setInputState(p1El, "input-wait");
  } else {
    if (msg) { msg.textContent = "비밀번호 조건을 만족하지 않습니다."; msg.style.color = "red"; }
    setInputState(p1El, "input-bad");
  }
}

function checkPasswordMatch() {
  const p1El = $("password1");
  const p2El = $("password2");
  const msg = $("pw_match_msg");

  const p1 = p1El?.value || "";
  const p2 = p2El?.value || "";

  if (!msg || !p1El || !p2El) return false;

  if (!p1 && !p2) { msg.textContent = ""; setInputState(p2El, null); return false; }
  if (!p2) { msg.textContent = ""; setInputState(p2El, null); return false; }

  const pwOk = isPasswordValid();
  const matchOk = p1 === p2;

  if (matchOk) { msg.textContent = "비밀번호가 일치합니다."; msg.style.color = "green"; }
  else { msg.textContent = "비밀번호가 다릅니다."; msg.style.color = "red"; }

  if (pwOk && matchOk) {
    setInputState(p1El, "input-ok");
    setInputState(p2El, "input-ok");
    return true;
  } else {
    if (!matchOk) setInputState(p2El, "input-bad");
    else setInputState(p2El, "input-ok");
    return false;
  }
}

function onPasswordInput() {
  updatePasswordRules();
  checkPasswordMatch();
  updateSubmitState();
}

/* ===============================
   ✅ 아이디/닉네임/이메일 실시간 중복확인
================================ */
let isIdChecked = false;
let isNickChecked = false;
let isEmailChecked = false;

let isCheckingId = false;
let isCheckingNick = false;
let isCheckingEmail = false;

let usernameTimer = null;
let nicknameTimer = null;
let emailTimer = null;

let lastAutoUsername = "";
let lastAutoNickname = "";
let lastAutoEmail = "";

// ---- 아이디 ----
function validateUsernameRuleAndExplain() {
  const input = $("username");
  const msg = $("id_check_msg");
  if (!input || !msg) return { ok: false, value: "" };

  const raw = input.value || "";
  const filtered = raw.replace(/[^A-Za-z0-9]/g, "");
  if (raw !== filtered) {
    input.value = filtered;
    msg.innerText = "영문과 숫자만 입력해 주세요.";
    msg.style.color = "red";
    setInputState(input, "input-bad");
  }

  const v = (input.value || "").trim();

  const okLen = v.length >= 6 && v.length <= 20;
  const okChar = /^[A-Za-z0-9]*$/.test(v);
  const okHasLetter = /[A-Za-z]/.test(v);
  const okHasNumber = /\d/.test(v);
  const okMix = okHasLetter && okHasNumber;

  const elLen = $("id_rule_len");
  const elChar = $("id_rule_char");
  const elMix = $("id_rule_mix");
  if (elLen) elLen.style.color = okLen ? "green" : "red";
  if (elChar) elChar.style.color = okChar ? "green" : "red";
  if (elMix) elMix.style.color = okMix ? "green" : "red";

  if (!v) { msg.innerText = ""; setInputState(input, null); return { ok: false, value: "" }; }

  const reasons = [];
  if (!okLen) reasons.push("아이디는 6~20자로 입력해 주세요.");
  if (okLen && okChar && !okMix) reasons.push("아이디는 영문과 숫자를 함께 포함해야 합니다.");

  if (reasons.length > 0) {
    msg.innerText = "❗ " + reasons[0];
    msg.style.color = "red";
    setInputState(input, "input-bad");
    return { ok: false, value: v };
  }

  msg.innerText = "확인 중...";
  msg.style.color = "#868e96";
  setInputState(input, "input-wait");
  return { ok: true, value: v };
}

function checkIdAuto() {
  usernameTimer = null;

  const rules = validateUsernameRuleAndExplain();
  const username = rules.value;
  const msg = $("id_check_msg");
  const input = $("username");

  if (!username || !rules.ok) {
    isIdChecked = false;
    isCheckingId = false;
    updateSubmitState();
    return;
  }

  if (lastAutoUsername === username) {
    isCheckingId = false;
    updateSubmitState();
    return;
  }
  lastAutoUsername = username;

  isCheckingId = true;
  msg.innerText = "확인 중...";
  msg.style.color = "#868e96";
  setInputState(input, "input-wait");
  updateSubmitState();

  fetch(`${CFG.checkIdUrl}?username=${encodeURIComponent(username)}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.exists) {
        msg.innerText = "이미 사용 중인 아이디입니다.";
        msg.style.color = "red";
        isIdChecked = false;
        setInputState(input, "input-bad");
        addOnceShake(input);
      } else {
        msg.innerText = "사용 가능한 아이디입니다.";
        msg.style.color = "green";
        isIdChecked = true;
        setInputState(input, "input-ok");
      }
    })
    .catch(() => {
      msg.innerText = "중복확인 중 오류가 발생했습니다.";
      msg.style.color = "red";
      isIdChecked = false;
      setInputState(input, "input-bad");
    })
    .finally(() => {
      isCheckingId = false;
      updateSubmitState();
    });
}

function onUsernameInput() {
  isIdChecked = false;
  isCheckingId = false;
  lastAutoUsername = "";

  validateUsernameRuleAndExplain();

  if (usernameTimer) clearTimeout(usernameTimer);
  usernameTimer = setTimeout(checkIdAuto, 600);

  updateSubmitState();
}

// ---- 닉네임 ----
function checkNicknameAuto() {
  nicknameTimer = null;

  const nickname = ($("nickname")?.value || "").trim();
  const msg = $("nickname_check_msg");
  const input = $("nickname");

  if (!msg || !input) return;

  if (!nickname) {
    msg.innerText = "";
    isNickChecked = false;
    isCheckingNick = false;
    setInputState(input, null);
    updateSubmitState();
    return;
  }

  if (nickname.length < 3) {
    msg.innerText = "❗ 닉네임은 3글자 이상 입력해 주세요.";
    msg.style.color = "red";
    isNickChecked = false;
    isCheckingNick = false;
    setInputState(input, "input-bad");
    updateSubmitState();
    return;
  }

  if (lastAutoNickname === nickname) {
    isCheckingNick = false;
    updateSubmitState();
    return;
  }
  lastAutoNickname = nickname;

  isCheckingNick = true;
  msg.innerText = "확인 중...";
  msg.style.color = "#868e96";
  setInputState(input, "input-wait");
  updateSubmitState();

  fetch(`${CFG.checkNicknameUrl}?nickname=${encodeURIComponent(nickname)}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.exists) {
        msg.innerText = "이미 사용 중인 닉네임입니다.";
        msg.style.color = "red";
        isNickChecked = false;
        setInputState(input, "input-bad");
        addOnceShake(input);
      } else {
        msg.innerText = "사용 가능한 닉네임입니다.";
        msg.style.color = "green";
        isNickChecked = true;
        setInputState(input, "input-ok");
      }
    })
    .catch(() => {
      msg.innerText = "중복확인 중 오류가 발생했습니다.";
      msg.style.color = "red";
      isNickChecked = false;
      setInputState(input, "input-bad");
    })
    .finally(() => {
      isCheckingNick = false;
      updateSubmitState();
    });
}

function onNicknameInput() {
  isNickChecked = false;
  isCheckingNick = false;
  lastAutoNickname = "";

  const nickname = ($("nickname")?.value || "").trim();
  const msg = $("nickname_check_msg");
  const input = $("nickname");
  if (!msg || !input) return;

  if (!nickname) {
    msg.innerText = "";
    setInputState(input, null);
  } else if (nickname.length < 3) {
    msg.innerText = "❗ 닉네임은 3글자 이상 입력해 주세요.";
    msg.style.color = "red";
    setInputState(input, "input-bad");
  } else {
    msg.innerText = "확인 중...";
    msg.style.color = "#868e96";
    setInputState(input, "input-wait");
  }

  if (nicknameTimer) clearTimeout(nicknameTimer);
  nicknameTimer = setTimeout(checkNicknameAuto, 600);

  updateSubmitState();
}

// ---- 이메일 ----
function isValidEmailFormat(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function checkEmailAuto() {
  emailTimer = null;

  const input = $("email");
  const msg = $("email_check_msg");
  if (!input || !msg) return;

  const email = (input.value || "").trim();

  if (!email) {
    msg.innerText = "";
    isEmailChecked = false;
    isCheckingEmail = false;
    setInputState(input, null);
    updateSubmitState();
    return;
  }

  if (!isValidEmailFormat(email)) {
    msg.innerText = "❗ 이메일 형식이 올바르지 않습니다.";
    msg.style.color = "red";
    isEmailChecked = false;
    isCheckingEmail = false;
    setInputState(input, "input-bad");
    updateSubmitState();
    return;
  }

  if (lastAutoEmail === email) {
    isCheckingEmail = false;
    updateSubmitState();
    return;
  }
  lastAutoEmail = email;

  isCheckingEmail = true;
  msg.innerText = "확인 중...";
  msg.style.color = "#868e96";
  setInputState(input, "input-wait");
  updateSubmitState();

  fetch(`${CFG.checkEmailUrl}?email=${encodeURIComponent(email)}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.exists) {
        msg.innerText = "이미 사용 중인 이메일입니다.";
        msg.style.color = "red";
        isEmailChecked = false;
        setInputState(input, "input-bad");
        addOnceShake(input);
      } else {
        msg.innerText = "사용 가능한 이메일입니다.";
        msg.style.color = "green";
        isEmailChecked = true;
        setInputState(input, "input-ok");
      }
    })
    .catch(() => {
      msg.innerText = "중복확인 중 오류가 발생했습니다.";
      msg.style.color = "red";
      isEmailChecked = false;
      setInputState(input, "input-bad");
    })
    .finally(() => {
      isCheckingEmail = false;
      updateSubmitState();
    });
}

function onEmailInput() {
  // ✅ 이메일 바뀌면: 중복확인/인증 모두 초기화
  isEmailChecked = false;
  isCheckingEmail = false;
  lastAutoEmail = "";
  resetEmailVerifyState();

  const input = $("email");
  const msg = $("email_check_msg");
  if (input && msg) {
    const email = (input.value || "").trim();
    if (!email) {
      msg.innerText = "";
      setInputState(input, null);
    } else if (!isValidEmailFormat(email)) {
      msg.innerText = "❗ 이메일 형식이 올바르지 않습니다.";
      msg.style.color = "red";
      setInputState(input, "input-bad");
    } else {
      msg.innerText = "확인 중...";
      msg.style.color = "#868e96";
      setInputState(input, "input-wait");
    }
  }

  if (emailTimer) clearTimeout(emailTimer);
  emailTimer = setTimeout(checkEmailAuto, 600);

  updateSubmitState();
}

/* ===============================
   ✅ 자녀 있음 / 없음 처리
================================ */
document.querySelectorAll('input[name="has_children_ui"]').forEach((el) => {
  el.addEventListener("change", () => {
    const hasChildren = el.value === "1";
    $("has_children").value = hasChildren ? "1" : "0";

    const box = $("childrenStageBox");
    if (box) box.style.display = hasChildren ? "block" : "none";

    const msg = $("children_stages_msg");
    if (!hasChildren) {
      document.querySelectorAll('input[name="children_stages"]').forEach((cb) => (cb.checked = false));
      if (msg) msg.textContent = "";
    } else {
      if (msg) msg.textContent = "자녀 학령을 최소 1개 선택해 주세요.";
    }

    updateSubmitState();
  });
});

document.querySelectorAll('input[name="children_stages"]').forEach((cb) => {
  cb.addEventListener("change", () => {
    const hasChildren = $("has_children")?.value === "1";
    const checkedCount = document.querySelectorAll('input[name="children_stages"]:checked').length;

    const msg = $("children_stages_msg");
    if (hasChildren && checkedCount === 0) {
      if (msg) msg.textContent = "자녀 학령을 최소 1개 선택해 주세요.";
    } else {
      if (msg) msg.textContent = "";
    }

    updateSubmitState();
  });
});

/* ===============================
   필수 입력 체크
================================ */
function isRequiredFilled() {
  mergeJumin();
  mergePhone();
  mergeAddress();

  const hasChildren = $("has_children")?.value === "1";
  const childrenChecked = document.querySelectorAll('input[name="children_stages"]:checked').length;

  const p1 = $("password1")?.value || "";
  const p2 = $("password2")?.value || "";

  const addressMain = ($("address_main")?.value || "").trim();
  const addressDetail = ($("address_detail")?.value || "").trim();

  const okPw = isPasswordValid();
  const okPwMatch = p1 && p2 && p1 === p2;

  return {
    username: ($("username")?.value || "").trim(),
    realName: ($("real_name")?.value || "").trim(),
    nickname: ($("nickname")?.value || "").trim(),
    jumin: ($("jumin")?.value || "").trim(),

    addressMain,
    addressDetail,

    phone: ($("phone")?.value || "").trim(),
    email: ($("email")?.value || "").trim(),

    okPw,
    okPwMatch,

    hasChildren,
    childrenOk: !hasChildren || childrenChecked > 0,

    terms: $("agree_terms")?.checked || false,
  };
}

/* ===============================
   가입 버튼 활성 제어
================================ */
function updateSubmitState() {
  const btn = $("submitBtn");
  if (!btn) return;

  const waiting =
    isCheckingId ||
    isCheckingNick ||
    isCheckingEmail ||
    usernameTimer !== null ||
    nicknameTimer !== null ||
    emailTimer !== null;

  const r = isRequiredFilled();

  const missing = [];
  if (!r.username) missing.push("아이디");
  if (!r.realName) missing.push("이름");
  if (!r.nickname) missing.push("닉네임");
  if (!r.jumin || r.jumin.length < 14) missing.push("주민번호");
  if (!r.addressMain) missing.push("주소 검색");
  else if (!r.addressDetail) missing.push("상세주소");
  if (!r.phone || r.phone.replace(/-/g, "").length < 10) missing.push("휴대폰");
  if (!r.email) missing.push("이메일");
  if (!r.okPw) missing.push("비밀번호");
  if (r.okPw && !r.okPwMatch) missing.push("비밀번호 확인");
  if (r.hasChildren && !r.childrenOk) missing.push("자녀 학령");
  if (!r.terms) missing.push("약관 동의");

  const canSubmit =
    r.terms &&
    missing.length === 0 &&
    isIdChecked &&
    isNickChecked &&
    isEmailChecked &&
    isEmailVerified &&
    !waiting;

  btn.disabled = !canSubmit;

  if (!r.terms) btn.textContent = "약관 동의 필요";
  else if (missing.length > 0) btn.textContent = `입력 필요: ${missing[0]}`;
  else if (waiting) btn.textContent = "중복확인 중...";
  else if (!isIdChecked) btn.textContent = "아이디 확인 필요";
  else if (!isNickChecked) btn.textContent = "닉네임 확인 필요";
  else if (!isEmailChecked) btn.textContent = "이메일 확인 필요";
  else if (!isEmailVerified) btn.textContent = "이메일 인증 필요";
  else btn.textContent = "가입하기";
}

/* ===============================
   ✅ 이메일 인증번호 발송/인증 (CSRF 쿠키)
================================ */
function getCSRFToken() {
  const name = "csrftoken=";
  const cookies = (document.cookie || "").split(";");
  for (let c of cookies) {
    c = c.trim();
    if (c.startsWith(name)) return decodeURIComponent(c.substring(name.length));
  }
  return "";
}

// ✅ 인증번호 보내기
$("btnSendCode")?.addEventListener("click", async () => {
  const emailInput = $("email");
  const statusEl = $("emailVerifyStatus");
  const sendBtn = $("btnSendCode");
  if (!emailInput || !sendBtn) return;

  // ✅ 추가
  const checkMsg = $("email_check_msg");
  if (checkMsg) checkMsg.textContent = "";

  const email = (emailInput.value || "").trim();

  // 발송 버튼 누르면 입력칸 표시
  showEmailCodeWrap();

  if (!email) { if (statusEl) statusEl.textContent = "이메일을 입력해 주세요."; return; }
  if (!isValidEmailFormat(email)) { if (statusEl) statusEl.textContent = "❗ 이메일 형식이 올바르지 않습니다."; return; }
  if (!isEmailChecked) { if (statusEl) statusEl.textContent = "이메일 중복확인을 먼저 완료해 주세요."; return; }

  const csrf = getCSRFToken();
  if (!csrf) { if (statusEl) statusEl.textContent = "CSRF 토큰을 못 찾았습니다. 새로고침 후 다시 시도해 주세요."; return; }

  sendBtn.disabled = true;
  if (statusEl) statusEl.textContent = "인증번호 발송 중...";

  try {
    const res = await fetch(CFG.sendEmailCodeUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": csrf,
      },
      body: new URLSearchParams({ email }),
    });

    const data = await res.json();
    if (data.ok) {
      if (statusEl) statusEl.textContent = "인증번호를 보냈어요! (개발: 터미널 확인)";
      isEmailVerified = false;
      updateSubmitState();
      $("emailCode")?.focus();
    } else {
      if (statusEl) statusEl.textContent = data.error || "발송 실패";
      isEmailVerified = false;
      updateSubmitState();
    }
  } catch (e) {
    if (statusEl) statusEl.textContent = "네트워크 오류로 발송 실패";
    isEmailVerified = false;
    updateSubmitState();
  } finally {
    sendBtn.disabled = false;
  }
});

// ✅ 인증하기
$("btnVerifyCode")?.addEventListener("click", async () => {
  const emailInput = $("email");
  const codeInput = $("emailCode");
  const statusEl = $("emailVerifyStatus");
  const verifyBtn = $("btnVerifyCode");
  if (!emailInput || !codeInput || !verifyBtn) return;

  const email = (emailInput.value || "").trim();
  const code = (codeInput.value || "").trim();

  if (!email || !code) { if (statusEl) statusEl.textContent = "이메일과 인증번호를 입력해 주세요."; return; }

  const csrf = getCSRFToken();
  if (!csrf) { if (statusEl) statusEl.textContent = "CSRF 토큰을 못 찾았습니다. 새로고침 후 다시 시도해 주세요."; return; }

  verifyBtn.disabled = true;
  if (statusEl) statusEl.textContent = "인증 중...";

  try {
    const res = await fetch(CFG.verifyEmailCodeUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": csrf,
      },
      body: new URLSearchParams({ email, code }),
    });

    const data = await res.json();

    if (data.ok) {
      markEmailVerified();
    } else {
      if (statusEl) statusEl.textContent = data.error || "인증 실패";
      isEmailVerified = false;
      updateSubmitState();
    }
  } catch (e) {
    if (statusEl) statusEl.textContent = "네트워크 오류로 인증 실패";
    isEmailVerified = false;
    updateSubmitState();
  } finally {
    verifyBtn.disabled = false;
  }
});

/* ===============================
   이벤트 바인딩
================================ */
$("username")?.addEventListener("input", onUsernameInput);
$("nickname")?.addEventListener("input", onNicknameInput);
$("email")?.addEventListener("input", onEmailInput);

$("password1")?.addEventListener("input", onPasswordInput);
$("password2")?.addEventListener("input", () => {
  checkPasswordMatch();
  updateSubmitState();
});

["real_name", "jumin1", "jumin2", "phone1", "phone2", "phone3", "address_detail"].forEach((id) => {
  $(id)?.addEventListener("input", updateSubmitState);
});

document.querySelectorAll('input[name="gender"]').forEach((el) =>
  el.addEventListener("change", updateSubmitState)
);

$("agree_terms")?.addEventListener("change", updateSubmitState);

/* ===============================
   폼 제출
================================ */
$("signupForm")?.addEventListener("submit", (e) => {
  saveDraft();

  mergeJumin();
  mergePhone();
  mergeAddress();
  updatePasswordRules();
  checkPasswordMatch();
  updateSubmitState();

  if ($("submitBtn")?.disabled) {
    alert($("submitBtn").textContent || "필수 입력 항목을 확인해 주세요.");
    e.preventDefault();
  }
});

/* ===============================
   초기화
================================ */
window.addEventListener("DOMContentLoaded", () => {
  // 숫자-only
  ["jumin1", "jumin2", "phone1", "phone2", "phone3"].forEach((id) => {
    $(id)?.addEventListener("input", (e) => onlyNumber(e.target));
  });

  // ✅ 이메일 인증 입력칸은 기본 숨김 (발송 후 show)
  hideEmailCodeWrap();

  restoreDraftIfServerErrors();

  updatePasswordRules();
  checkPasswordMatch();

  validateUsernameRuleAndExplain();
  if (($("username")?.value || "").trim()) onUsernameInput();
  if (($("nickname")?.value || "").trim()) onNicknameInput();
  if (($("email")?.value || "").trim()) onEmailInput();

  $("has_children") && ($("has_children").value = $("has_children").value || "0");
  updateSubmitState();
});
