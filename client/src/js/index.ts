class ToggleElement {
  buttonSelector: string;
  constructor() {
    this.buttonSelector = "[data-toggle-element]";
    document
      .querySelectorAll(this.buttonSelector)
      .forEach(this.initComponent, this);
  }

  toggleEl(targetId) {
    const el = document.getElementById(targetId);
    if (el) {
      if (el.classList.contains("hide") ) {
        el.classList.remove("hide");
      } else{
        el.classList.add("hide")
      }
    }
  }

  initComponent(el) {
    const targetId = el.getAttribute("data-toggle-element");
    el.addEventListener("click", (evt) => {
      evt.preventDefault();
      this.toggleEl(targetId);
    });
  }
}

function initComponents() {
  new ToggleElement()
}

export {
  initComponents,
  ToggleElement,
}
