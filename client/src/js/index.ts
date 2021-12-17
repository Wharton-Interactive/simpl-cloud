class ToggleElement {
  buttonAttr: string;
  constructor() {
    this.buttonAttr = "data-toggle-elements";
    document
      .querySelectorAll(`[${this.buttonAttr}]`)
      .forEach(this.initComponent, this);
  }

  toggleEl(targetSelector: string) {
    document.querySelectorAll(targetSelector).forEach((el: Element) => {
      if (el.classList.contains("hide")) {
        el.classList.remove("hide");
      } else {
        el.classList.add("hide")
      }
    })
  }

  initComponent(el) {
    const targetSelector = el.getAttribute(this.buttonAttr);
    el.addEventListener("click", (evt: Event) => {
      evt.preventDefault();
      this.toggleEl(targetSelector);
    });
  }
}

class ExpandCollapse {
  collapsibleAttr: string;
  toggleButtonAttr: string;
  collapseAllAttr: string;
  expandAllAttr: string;
  toggleButtons: any[] | NodeListOf<Element>;
  allCollapsibles: any[] | NodeListOf<Element>;
  expandAllButtons: any[] | NodeListOf<Element>;
  collapseAllButtons: any[] | NodeListOf<Element>;

  constructor() {
    this.collapsibleAttr = "data-is-accordion";
    this.toggleButtonAttr = "data-toggle-collapsible";
    this.expandAllAttr = "data-expand-all";
    this.collapseAllAttr = "data-collapse-all";

    this.allCollapsibles = document.querySelectorAll(`[${this.collapsibleAttr}]`);
    this.toggleButtons = document.querySelectorAll(`[${this.toggleButtonAttr}]`);
    this.expandAllButtons = document.querySelectorAll(`[${this.expandAllAttr}]`);
    this.collapseAllButtons = document.querySelectorAll(`[${this.collapseAllAttr}]`);

    this.toggleButtons.forEach(
      (button) => button.addEventListener(
        "click", (evt) => this.toggleCollapsible(button)));
    this.expandAllButtons.forEach(
      (button) => button.addEventListener(
        "click", (evt) => this.expandAll()));
    this.collapseAllButtons.forEach(
      (button) => button.addEventListener(
        "click", (evt) => this.collapseAll()));
  }

  hide(el: Element) {
    el.classList.add("hide");
  }

  show(el: Element) {
    el.classList.remove("hide");
  }

  toggle(el: Element) {
    el.classList.toggle('hide')
  }

  setExpanded(el: Element) {
    el.classList.add("is-expanded");
  }

  removeExpanded(el: Element) {
    el.classList.remove("is-expanded");
  }

  toggleCollapsible(button: Element) {
    const targetSelector = button.getAttribute(this.toggleButtonAttr);
    document.querySelectorAll(targetSelector).forEach((target) => this.toggle(target));
    button.classList.toggle('is-expanded');
  }

  expandAll() {
    this.expandAllButtons.forEach((el: Element) => this.hide(el));
    this.collapseAllButtons.forEach((el: Element) => this.show(el));
    this.allCollapsibles.forEach((el: Element) => this.show(el));
    this.toggleButtons.forEach((el: Element) => this.setExpanded(el));
  }

  collapseAll() {
    this.collapseAllButtons.forEach((el: Element) => this.hide(el));
    this.expandAllButtons.forEach((el: Element) => this.show(el));
    this.allCollapsibles.forEach((el: Element) => this.hide(el));
    this.toggleButtons.forEach((el: Element) => this.removeExpanded(el));
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

  initComponent(el: Element) {
    const timeOut = parseInt(el.getAttribute("data-timeout")) || 5000;
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
  checkbox: Element;
  willDisable: Element;
  willDisableFields: NodeListOf<Element>;

  constructor() {
    this.selector = ".field-pair";
    document
      .querySelectorAll(this.selector)
      .forEach(this.initComponent, this);
  }

  toggleCheckboxes(el: Element) {
    this.checkbox = el.querySelector("[type=checkbox]");
    this.willDisable = el.querySelector("[data-disabled-when-unchecked]");
    this.willDisableFields = this.willDisable.querySelectorAll('input');
    let isChecked = !!el.querySelector("[data-disable-fields]:checked");

    if (isChecked) {
      this.willDisableFields.forEach((el) => el.removeAttribute('disabled'));
    } else {
      this.willDisableFields.forEach((el) => el.setAttribute('disabled', 'disabled'));
    }

    this.willDisable.classList.toggle('is-disabled', !isChecked);
    el.classList.toggle("has-checked", isChecked);
  }

  initComponent(el: Element) {
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
  new ExpandCollapse();
}

export {
  initComponents,
  Toast,
  ToggleElement,
  CheckboxEnhancement,
  ExpandCollapse,
}
