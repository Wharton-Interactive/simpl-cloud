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

class Toast {
  selector: string;
  constructor() {
    this.selector = "[data-toast]";
    document
      .querySelectorAll(this.selector)
      .forEach(this.initComponent, this);
  }

  initComponent(el) {
    const timeOut = el.getAttribute("data-timeout") || 5000;
    setTimeout(() => {
      if (el.classList.contains("collapse")) {
        el.classList.remove("in")
      } else {
        el.classList.add("hide")
      }
    }, timeOut);
  }
}

function initComponents() {
  new ToggleElement();
  new Toast();
}

export {
  initComponents,
  Toast,
  ToggleElement,
}