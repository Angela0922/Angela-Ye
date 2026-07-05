(function () {
  var params = new URLSearchParams(window.location.search);
  var appUrl = params.get("app") || "http://localhost:8501";
  var selectedDoll = params.get("doll") || "wren";

  var nameInput = document.getElementById("child-name");
  var preview = document.getElementById("story-preview");
  var previewName = document.getElementById("preview-name");
  var previewDoll = document.getElementById("preview-doll");
  var cards = document.querySelectorAll(".friend-card[data-doll]");

  function dollLabel(id) {
    return id.charAt(0).toUpperCase() + id.slice(1);
  }

  function updatePreview() {
    var name = nameInput && nameInput.value.trim();
    if (name && preview && previewName && previewDoll) {
      previewName.textContent = name;
      previewDoll.textContent = dollLabel(selectedDoll);
      preview.hidden = false;
    } else if (preview) {
      preview.hidden = true;
    }
  }

  cards.forEach(function (card) {
    if (card.dataset.doll === selectedDoll) {
      card.classList.add("selected");
    }
    card.addEventListener("click", function () {
      cards.forEach(function (c) { c.classList.remove("selected"); });
      card.classList.add("selected");
      selectedDoll = card.dataset.doll;
      updatePreview();
    });
  });

  if (nameInput) {
    nameInput.addEventListener("input", updatePreview);
    var preset = params.get("name");
    if (preset) {
      nameInput.value = preset;
      updatePreview();
    }
  }

  function goToApp(event) {
    event.preventDefault();
    var name = nameInput && nameInput.value.trim();
    var url = appUrl;
    var qs = [];
    if (name) qs.push("name=" + encodeURIComponent(name));
    if (selectedDoll) qs.push("doll=" + encodeURIComponent(selectedDoll));
    if (qs.length) url += (url.indexOf("?") >= 0 ? "&" : "?") + qs.join("&");
    window.location.href = url;
  }

  document.querySelectorAll("[data-app-link]").forEach(function (el) {
    el.addEventListener("click", goToApp);
    el.href = appUrl;
  });

  updatePreview();
})();
