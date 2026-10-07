/* Connectly – frontend behaviour (vanilla JS) */
(function () {
  "use strict";

  // ---------- Toast helper ----------
  const toastEl = document.getElementById("toast");
  let toastTimer;
  function showToast(message, isError) {
    if (!toastEl) return;
    toastEl.textContent = message;
    toastEl.classList.toggle("error", !!isError);
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("show"), 2500);
  }

  async function postForm(form) {
    const response = await fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: { "X-Requested-With": "XMLHttpRequest" },
      credentials: "same-origin",
    });
    if (!response.ok) throw new Error("Request failed");
    return response.json();
  }

  // ---------- Mobile navigation ----------
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");
  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => {
      const open = navLinks.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", String(open));
    });
  }

  // ---------- Auto-hide Django messages ----------
  document.querySelectorAll(".messages .alert").forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity .4s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // ---------- Like / Follow toggles via AJAX ----------
  document.addEventListener("submit", async (e) => {
    const form = e.target;

    if (form.classList.contains("js-like")) {
      e.preventDefault();
      const btn = form.querySelector(".like-btn");
      try {
        const data = await postForm(form);
        btn.classList.toggle("liked", data.liked);
        btn.setAttribute("aria-pressed", String(data.liked));
        btn.querySelector(".icon").textContent = data.liked ? "❤️" : "🤍";
        btn.querySelector(".count").textContent = data.like_count;
        btn.classList.add("pop");
        setTimeout(() => btn.classList.remove("pop"), 200);
      } catch (err) {
        form.submit(); // graceful fallback
      }
      return;
    }

    if (form.classList.contains("js-follow")) {
      e.preventDefault();
      const btn = form.querySelector("button");
      btn.disabled = true;
      try {
        const data = await postForm(form);
        btn.textContent = data.following ? "Following" : "Follow";
        btn.classList.toggle("btn-outline", data.following);
        btn.classList.toggle("following", data.following);
        btn.dataset.following = String(data.following);
        document.querySelectorAll(".js-followers-count").forEach((el) => (el.textContent = data.followers_count));
        showToast(data.following ? "You are now following this user." : "Unfollowed.");
      } catch (err) {
        form.submit();
      } finally {
        btn.disabled = false;
      }
    }
  });

  // ---------- Compose box: character counter + image preview ----------
  const composeText = document.querySelector(".compose textarea");
  const charCount = document.getElementById("charCount");
  if (composeText && charCount) {
    const update = () => (charCount.textContent = composeText.value.length);
    composeText.addEventListener("input", update);
    update();
  }

  const imageInput = document.getElementById("postImage");
  const preview = document.getElementById("imagePreview");
  const removeBtn = document.getElementById("removeImage");
  if (imageInput && preview) {
    imageInput.addEventListener("change", () => {
      const file = imageInput.files && imageInput.files[0];
      if (!file) { preview.hidden = true; return; }
      preview.querySelector("img").src = URL.createObjectURL(file);
      preview.hidden = false;
    });
    removeBtn && removeBtn.addEventListener("click", () => {
      imageInput.value = "";
      preview.hidden = true;
    });
  }
})();
