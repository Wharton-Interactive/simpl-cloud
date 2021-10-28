class ToggleElement {
  buttonAttr: string;
  constructor() {
    this.buttonAttr = "data-toggle-elements";
    document
      .querySelectorAll(`[${this.buttonAttr}]`)
      .forEach(this.initComponent, this);
  }

  toggleEl(targetSelector) {
    document.querySelectorAll(targetSelector).forEach((el) => {
      if (el.classList.contains("hide") ) {
        el.classList.remove("hide");
      } else{
        el.classList.add("hide")
      }
    })
  }

  initComponent(el) {
    const targetSelector = el.getAttribute(this.buttonAttr);
    el.addEventListener("click", (evt) => {
      evt.preventDefault();
      this.toggleEl(targetSelector);
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
