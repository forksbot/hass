class AfterShipCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  setConfig(config) {
    if (!config.entity) {
      throw new Error('Please define a entity');
    }
    const root = this.shadowRoot;
    if (root.lastChild) root.removeChild(root.lastChild);

    const cardConfig = Object.assign({}, config);
    if (!cardConfig.title) {
      cardConfig.title = 'Aftership tracking';
    } else {
      cardConfig.title = cardConfig.title;
    }
    const card = document.createElement('ha-card');
    const content = document.createElement('div');
    const style = document.createElement('style');
    style.textContent = `
          ha-card {
            /* sample css */
          }
          table {
            width: 100%;
            padding: 0 32px 32px 32px;
          }
          thead th {
            text-align: left;
          }
          tbody tr:nth-child(odd) {
            background-color: var(--paper-card-background-color);
          }
          tbody tr:nth-child(even) {
            background-color: var(--secondary-background-color);
          }
          td a {
            color: var(--primary-text-color);
            text-decoration-line: none;
            font-weight: normal;
          }
          .button {
            overflow: auto;
            padding: 16px;
          }
          paper-button {
            float: right;
          }
          input {
            max-width: 75px;
          }
        `;
    content.innerHTML = `
      <div id='AfterShip'>
      </div>
      <div class='button'>
        <paper-button raised id='add_tracking'>Add Tracking</paper-button>
      </div>
    `;
    card.header = cardConfig.title
    card.appendChild(content);
    card.appendChild(style);
    root.appendChild(card);
    this._config = cardConfig;
  }
  // Hide attributes we do not want to show
  _filterCards(attributes) {
    return Object.entries(attributes).filter(elem => (elem[0] != "friendly_name" && elem[0] != "homebridge_hidden" && elem[0] != "icon" && elem[0] != "hidden"));
  }

  set hass(hass) {
    const config = this._config;
    const root = this.shadowRoot;
    const card = root.lastChild;
    this.myhass = hass;
    this.handlers = this.handlers || [];
    let card_content = '';
    card_content += `
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Status</th>
            <th>Tracking Number (slug)</th>
          </tr>
        </thead>
      <tbody>
    `;
      if (hass.states[this._config.entity]) {
        const list = this._filterCards(hass.states[this._config.entity].attributes);

        if (list !== undefined && list.length > 0) {
          const updated_content = `
            ${list.map(elem => `
                <tr>
                  <td>${elem[1].title}</td>
                  <td>${elem[1].status}</td>
                  <td><a href="https://track.aftership.com/${elem[1].slug}/${elem[0]}" target='_blank'>${elem[0]} (${elem[1].slug})</a></td>
                </tr>
            `).join('')}
          `;
          card_content += updated_content;
          card_content += `
            <tr>
              <td><input type="text" name="title" placeholder="Title"></td>
              <td><input type="text" name="slug" placeholder="Slug"></td>
              <td><input type="text" name="tracking_number" placeholder="Tracking #"></td>
            </tr>
          `;
        }

        // attach handlers only once
        if (!this.handlers['aftership']) {
          card.querySelector('#add_tracking').addEventListener('click', event => {
            console.log("got click");
            // if (title && slug && tracking_number) {
            //   this.myhass.callService('sensor', 'aftership_add_tracking',
            //   {
            //     "title": title,
            //     "slug": slug,
            //     "tracking_number": tracking_number
            //   });
            // } else {
            //   throw new Error('Invalid parameters for adding new AfterShip tracking. Please verify inputs.');
            // }
          });
          this.handlers['aftership'] = true;
        }

        root.lastChild.hass = hass;
      };
    
    card_content += `</tbody></table>`;
    root.getElementById('AfterShip').innerHTML = card_content;

  }
  getCardSize() {
    return 1;
  }
}
customElements.define('aftership-card', AfterShipCard);