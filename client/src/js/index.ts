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

class CheckboxEnhancement {
  selector: string;
  constructor() {
    this.selector = ".field-pair";
    document
      .querySelectorAll(this.selector)
      .forEach(this.initComponent, this);
  }

  toggleCheckboxes(el){
    this.checkbox = el.querySelector("[type=checkbox]");
    this.willDisable = el.querySelector("[data-disabled-when-unchecked]");
    this.willDisableField = this.willDisable.querySelector('input');
    let isChecked = el.querySelector(":checked");

    if (isChecked) {
      this.willDisableField.removeAttribute('disabled');
    } else {
      this.willDisableField.setAttribute('disabled', 'disabled');
    }

    this.willDisable.classList.toggle('is-disabled', !isChecked);
    el.classList.toggle("has-checked", isChecked);
  }

  initComponent(el) {
    this.toggleCheckboxes(el);

    this.checkbox.addEventListener("change", () => {
      this.toggleCheckboxes(el);
    });
  }
}

function initComponents() {
  new ToggleElement();
  new Toast();
  new CheckboxEnhancement();
}

export {
  initComponents,
  Toast,
  ToggleElement,
  CheckboxEnhancement,
}
