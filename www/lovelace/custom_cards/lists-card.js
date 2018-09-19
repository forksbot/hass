
class ListsCard extends HTMLElement {

    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
    }

    setConfig(config) {
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
      let card_content = ``;
      this.style.display = 'block';
      this.lists = {};
      hass.callApi('get', 'lists')
        .then(function (lists) {
          // lists.reverse();
          this.lists = lists;
          console.log(lists);
        }.bind(this));

      //   <paper-tabs selected="[[tab]]" scrollable>
      //   <paper-tab>Inbox</paper-tab>
      //   <paper-tab>Grocery</paper-tab
      // </paper-tabs>
      // <iron-pages selected="[[tab]]">
      //   <div>Page 1</div>
      //   <div>Page 2</div>
      //   <div>Page 3</div>
      // </iron-pages>
      card_content += `

      <div>
        <paper-dropdown-menu label="Lists">
        <paper-listbox slot="dropdown-content" selected="0">
            <paper-item>Inbox</paper-item>
            <paper-item>Grocery</paper-item>
            <paper-item>Todos</paper-item>
            <paper-item>Work</paper-item>
          </paper-listbox>
        </paper-dropdown-menu>
        <paper-menu-button
          horizontal-align="right"
          horizontal-offset="-5"
          vertical-offset="-5"
        >
          <paper-icon-button
            icon="hass:dots-vertical"
            slot="dropdown-trigger"
          ></paper-icon-button>
          <paper-listbox slot="dropdown-content">
            <paper-item on-click="_refreshList">
              <paper-icon-button icon="mdi:refresh"></paper-icon-button>
              Refresh
            </paper-item>
            <paper-item on-click="_clearCompleted">
              <paper-icon-button icon="mdi:playlist-check"></paper-icon-button>
              Clear
            </paper-item>
          </paper-listbox>
        </paper-menu-button>
      </div>

      <div class='content'>
        <paper-card>
          <paper-icon-item on-focus='_focusRowInput'>
            <paper-icon-button
              slot="item-icon"
              icon="hass:plus"
              on-click='_addItem'
            ></paper-icon-button>
            <paper-item-body>
              <paper-input
                id='addBox'
                placeholder="Add Item"
                on-keydown='_addKeyPress'
                no-label-float
              ></paper-input>
            </paper-item-body>
          </paper-icon-item>

          <template is='dom-repeat' lists='[[lists]]'>
            <paper-icon-item>
              <paper-checkbox
                slot="item-icon"
                checked='{{item.complete}}'
                on-click='_itemCompleteTapped'
                tabindex='0'
              ></paper-checkbox>
              <paper-item-body>
                <paper-input
                  id='editBox'
                  no-label-float
                  value='[[list.name]]'
                  on-change='_saveEdit'
                ></paper-input>
              </paper-item-body>
            </paper-icon-item>
          </template>
        </paper-card>
      </div>`;
      root.lastChild.hass = hass;
      root.getElementById('container').innerHTML = card_content;
    }

    getCardSize() {
      return 1;
    }

    _fetchData() {
      this.hass.callApi('get', 'lists')
        .then(function (lists) {
          lists.reverse();
          this.lists = lists;
          console.log(lists);
        }.bind(this));
    }
  }

  customElements.define('lists-card', ListsCard);