const CFG = window.MYPAGE_DELETE_CONFIG || {};
const $ = (id) => document.getElementById(id);

let pwTimer = null;
let pwMatched = false;

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

function canSubmit() {
  const agree = $("deleteAgree");
  return pwMatched && !!(agree && agree.checked);
}

function refreshSubmit() {
  const btn = $("deleteSubmitBtn");
  if (!btn) return;
  btn.disabled = !canSubmit();
}

async function checkPassword() {
  const input = $("deletePassword");
  const msg = $("deletePwMsg");
  if (!input || !msg) return;

  const pw = (input.value || "").trim();
  if (!pw) {
    pwMatched = false;
    setInputState(input, msg, "", "muted");
    refreshSubmit();
    return;
  }

  try {
    const res = await fetch(CFG.checkOldPasswordUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-CSRFToken": getCsrfToken(),
      },
      body: new URLSearchParams({ old_password: pw }).toString(),
      credentials: "same-origin",
    });

    const data = await res.json();

    if (!data.ok) {
      pwMatched = false;
      setInputState(input, msg, "비밀번호 재확인이 필요해요. 다시 들어와 주세요.", "bad");
      refreshSubmit();
      return;
    }

    pwMatched = !!data.matched;

    if (pwMatched) {
      setInputState(input, msg, "현재 비밀번호가 확인되었습니다.", "ok");
    } else {
      setInputState(input, msg, "현재 비밀번호가 올바르지 않습니다.", "bad");
    }

    refreshSubmit();
  } catch (e) {
    pwMatched = false;
    setInputState(input, msg, "비밀번호 확인 중 오류가 발생했습니다.", "bad");
    refreshSubmit();
  }
}

function getCsrfToken() {
  const el = document.querySelector("input[name=csrfmiddlewaretoken]");
  return el ? el.value : "";
}

function bindToggleEye() {
  document.querySelectorAll(".toggle-eye").forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.toggleTarget;
      const input = document.getElementById(targetId);
      if (!input) return;

      const isPw = input.type === "password";
      input.type = isPw ? "text" : "password";
      btn.textContent = isPw ? "숨김" : "표시";
    });
  });
}

function bindEvents() {
  const pwInput = $("deletePassword");
  const agree = $("deleteAgree");

  if (pwInput) {
    pwInput.addEventListener("input", () => {
      if (pwTimer) clearTimeout(pwTimer);
      pwTimer = setTimeout(checkPassword, 300);
    });
    pwInput.addEventListener("blur", checkPassword);
  }

  if (agree) {
    agree.addEventListener("change", refreshSubmit);
  }

  refreshSubmit();
}

document.addEventListener("DOMContentLoaded", () => {
  bindToggleEye();
  bindEvents();
});
