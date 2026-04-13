const CFG = window.MYPAGE_PASSWORD_CONFIG || {};
const $ = (id) => document.getElementById(id);

let oldPwTimer = null;

function setInputState(inputEl, msgEl, text, type) {
  if (!inputEl || !msgEl) return;

  inputEl.classList.remove("is-ok", "is-bad");
  msgEl.classList.remove("msg-ok", "msg-bad", "msg-muted");

  msgEl.textContent = text || "";

  if (type === "ok") {
    inputEl.classList.add("is-ok");
    msgEl.classList.add("msg-ok");
  } else if (type === "bad") {
    inputEl.classList.add("is-bad");
    msgEl.classList.add("msg-bad");
  } else {
    msgEl.classList.add("msg-muted");
  }
}

async function postForm(url, dataObj) {
  const csrf = document.querySelector("input[name=csrfmiddlewaretoken]")?.value || "";
  const body = new URLSearchParams(dataObj);

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
      "X-CSRFToken": csrf,
    },
    body,
  });

  return await res.json();
}

function bindOldPasswordCheck() {
  const oldInput = $("id_old_password");
  const msg = $("oldPwMsg");
  if (!oldInput || !msg || !CFG.checkOldPasswordUrl) return;

  oldInput.addEventListener("input", () => {
    clearTimeout(oldPwTimer);

    const v = (oldInput.value || "").trim();
    if (!v) {
      setInputState(oldInput, msg, "", "muted");
      return;
    }

    setInputState(oldInput, msg, "확인 중...", "muted");

    oldPwTimer = setTimeout(async () => {
      try {
        const data = await postForm(CFG.checkOldPasswordUrl, { old_password: v });
        if (!data.ok) {
          setInputState(oldInput, msg, "확인할 수 없습니다. 다시 시도해 주세요.", "bad");
          return;
        }
        if (data.matched) {
          setInputState(oldInput, msg, "비밀번호가 일치합니다.", "ok");
        } else {
          setInputState(oldInput, msg, "비밀번호가 불일치합니다.", "bad");
        }
      } catch (e) {
        setInputState(oldInput, msg, "확인 중 오류가 발생했습니다.", "bad");
      }
    }, 350);
  });
}

function hasLetter(s) { return /[A-Za-z]/.test(s); }
function hasNumber(s) { return /\d/.test(s); }
function hasSpecial(s) { return /[^A-Za-z0-9]/.test(s); }

function isPasswordValid(pw) {
  const okLen = pw.length >= 8;
  const okMix = hasLetter(pw) && hasNumber(pw) && hasSpecial(pw);
  return okLen && okMix;
}

function bindNewPasswordMatch() {
  const oldPw = $("id_old_password");
  const pw1 = $("id_new_password1");
  const pw2 = $("id_new_password2");
  const ruleMsg = $("newPwRuleMsg");
  const matchMsg = $("newPwMsg");

  if (!oldPw || !pw1 || !pw2 || !ruleMsg || !matchMsg) return;

  const check = () => {
    const oldVal = (oldPw.value || "").trim();
    const a = (pw1.value || "").trim();
    const b = (pw2.value || "").trim();

    // 초기화
    ruleMsg.textContent = "";
    matchMsg.textContent = "";
    ruleMsg.className = "field__msg";
    matchMsg.className = "field__msg";

    pw1.classList.remove("is-ok", "is-bad");
    pw2.classList.remove("is-ok", "is-bad");

    // 아무것도 입력 안 된 상태
    if (!a && !b) return;

    // ✅ 1. 기존 비밀번호와 동일한 경우 (최우선)
    if (oldVal && a && oldVal === a) {
      ruleMsg.textContent = "기존에 사용하던 비밀번호는 사용할 수 없어요.";
      ruleMsg.classList.add("msg-bad");
      pw1.classList.add("is-bad");

      if (b) {
        pw2.classList.add("is-bad");
        matchMsg.textContent = "새 비밀번호를 다시 설정해 주세요.";
        matchMsg.classList.add("msg-bad");
      }
      return;
    }

    // ✅ 2. 새 비밀번호 규칙 검사
    if (a) {
      const ruleOk = isPasswordValid(a);
      if (ruleOk) {
        ruleMsg.textContent = "좋아요! 조건을 만족하는 비밀번호예요.";
        ruleMsg.classList.add("msg-ok");
        pw1.classList.add("is-ok");
      } else {
        ruleMsg.textContent = "비밀번호 조건을 만족하지 않습니다. 다시 입력해 주세요.";
        ruleMsg.classList.add("msg-bad");
        pw1.classList.add("is-bad");
      }
    }

    // 확인칸 비어있으면 여기까지
    if (!b) return;

    // ✅ 3. 새 비밀번호 / 확인 일치 검사
    if (a === b) {
      matchMsg.textContent = "비밀번호가 일치합니다.";
      matchMsg.classList.add("msg-ok");
      pw2.classList.add("is-ok");
    } else {
      matchMsg.textContent = "비밀번호가 일치하지 않습니다.";
      matchMsg.classList.add("msg-bad");
      pw2.classList.add("is-bad");
    }
  };

  oldPw.addEventListener("input", check);
  pw1.addEventListener("input", check);
  pw2.addEventListener("input", check);
}


document.addEventListener("click", (e) => {
  const btn = e.target.closest(".toggle-eye");
  if (!btn) return;

  const targetId = btn.dataset.toggleTarget;
  const input = document.getElementById(targetId);
  if (!input) return;

  const isPw = input.type === "password";
  input.type = isPw ? "text" : "password";
  btn.textContent = isPw ? "숨김" : "표시";
  input.focus();
});


document.addEventListener("DOMContentLoaded", () => {
  bindOldPasswordCheck();
  bindNewPasswordMatch();
});
