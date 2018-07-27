class MarqueeStateElement extends HTMLElement {
  set hass(hass) {
    const entityId = this.config.entity;
    const state = hass.states[entityId];
    const stateStr = state ? state.state : 'unavailable';

    const card = document.createElement('marquee-state-element');
    this.innerHTML = `
      <marquee>${stateStr}</marquee>
    `;
  }
  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity');
    }
    this.config = config;
  }

  getCardSize() {
    return 1;
  }
}

customElements.define('marquee-state-element', MarqueeStateElement);