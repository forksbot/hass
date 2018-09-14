class ListsCard extends HTMLElement {

    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
    }

    setConfig(config) {
      if (!config.entity) {
        throw new Error('Please define an entity');
      }

      const root = this.shadowRoot;
      if (root.lastChild) root.removeChild(root.lastChild);

      const cardConfig = Object.assign({}, config);
      const card = document.createElement('ha-card');
      const content = document.createElement('div');
      const style = document.createElement('style');
      style.textContent = `
            ha-card {
              /* sample css */
            }
            table {
              width: 100%;
              padding: 0 32px 0 32px;
            }
            th {
              text-align: left;
            }
            tbody tr:nth-child(odd) {
              background-color: var(--paper-card-background-color);
            }
            tbody tr:nth-child(even) {
              background-color: var(--secondary-background-color);
            }
            .button {
              overflow: auto;
              padding: 16px;
            }
            paper-button {
              float: right;
            }
            td a {
              color: var(--primary-text-color);
              text-decoration-line: none;
              font-weight: normal;
            }
          `;

      content.id = "container";
      card.header = "Lists";
      card.appendChild(content);
      card.appendChild(style);
      root.appendChild(card);
      this._config = cardConfig;
    }

    set hass(hass) {
      const config = this._config;
      const root = this.shadowRoot;
      const card = root.lastChild;
      this.style.display = 'block';
      // root.getElementById('container').innerHTML = card_content;
    }

    getCardSize() {
      return 1;
    }
  }

  customElements.define('lists-card', ListsCard);