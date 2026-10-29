const slides = {};
window.STORY.forEach((s) => { slides[s.id] = s; });
const firstId = window.STORY[0].id;

const imageEl = document.getElementById("slide-image");
const textEl = document.getElementById("slide-text");
const actionsEl = document.getElementById("slide-actions");

// Échappe le HTML puis interprète le gras (**…**) et l'italique (*…*) du fichier source.
function inline(text) {
  return text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
}

function paragraphs(list) {
  return list.map((p) => `<p>${inline(p)}</p>`).join("");
}

function button(className, html, onClick) {
  const b = document.createElement("button");
  b.className = className;
  b.innerHTML = html;
  b.addEventListener("click", onClick);
  return b;
}

function show(id) {
  const slide = slides[id] || slides[firstId];
  imageEl.src = `images/page-${slide.id}.svg`;
  textEl.innerHTML = paragraphs(slide.text);
  textEl.classList.toggle("big", slide.end || slide.id === firstId);
  actionsEl.innerHTML = "";

  if (slide.choices) {
    slide.choices.forEach((c, i) => {
      if (i > 0) {
        const or = document.createElement("div");
        or.className = "or";
        or.textContent = "OU";
        actionsEl.appendChild(or);
      }
      const html = `<span class="choice-label">${inline(c.label)}</span>${paragraphs(c.text)}`;
      actionsEl.appendChild(button("choice", html, () => go(c.target)));
    });
  } else if (slide.end) {
    actionsEl.appendChild(button("btn-restart", "Revenir au début", () => go(firstId)));
  } else {
    actionsEl.appendChild(button("btn-next", "Suite →", () => go(slide.next)));
  }
}

function go(id) {
  location.hash = id;
}

window.addEventListener("hashchange", () => {
  show(location.hash.slice(1));
  window.scrollTo(0, 0);
});
show(location.hash.slice(1));
