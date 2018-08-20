class HorizontalScrollCard extends HTMLElement {
  constructor() {
    super();
    // Make use of shadowRoot to avoid conflicts when reusing
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>


      #columns {
        flex-direction: row;
        justify-content: center;
        max-width: 4000px;
        overflow-y: hidden;
        overflow-x: scroll;
        height: 250px;
        max-height: 250px;

      }

      .column {
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: row;
      }

      .column > * {
        flex: 0 0 auto;
        width: 400px;
        height: 100px;
        margin: 10px;
        opacity: 0;
        animation: easeDown 1000ms cubic-bezier(.1, .80, .44, .96) 0ms forwards;
      }

      @-webkit-keyframes easeDown {
          0% {
              transform: translateY(-50px);
              opacity:0;
          }
          100% {
              transform: translateY(0px);
              opacity:1;
          }
      }

      ::-webkit-scrollbar {
        display: none;
      }

      </style>
      `;

    this.cols = document.createElement('div');
    this.cols.setAttribute("id", "columns");
    this.shadowRoot.appendChild(this.cols);
    
    

    this.columns = 0;
    this._cards = [];
  }

  setConfig(config) {
    this.config = config;
    if (!config || !config.cards || !Array.isArray(config.cards)) {
      throw new Error('Card config incorrect');
    }
    const cardConfig = Object.assign({}, config);
    
    
    
    // if (!cardConfig.item_height) cardConfig.item_height = '250px';


    // The cards are created here in order to allow finding their height later
    // hui-view.js recreated the cards whenever the number of columns change, but that didn't work for me.
    // There might be some bad side effects of this, but I haven't encountered any so far.
    // Heads up, though...
    this._cards = config.cards.map((item) => {
      let element;
      if (item.type.startsWith("custom:")){
        element = document.createElement(`${item.type.substr("custom:".length)}`);
      } else {
        element = document.createElement(`hui-${item.type}-card`);
      }
      element.setConfig(item);
      if(this.hass)
        element.hass = this.hass;
      return element;
    });

    window.addEventListener('resize', (event) => {this._updateColumns()});
    window.setTimeout((event) => {this._updateColumns()}, 10);
  }

  _updateColumns() {
    let numcols = Math.max(1,Math.floor(this.cols.clientWidth/3000));
    if(numcols != this.columns) {
      this.columns = numcols
      this._createColumns();
    }
    
    
  }

  _createColumns() {
    // This code is copied more or less verbatim from hui-view.js in home-assistant.
    // https://github.com/home-assistant/home-assistant-polymer/blob/master/src/panels/lovelace/hui-view.js
    // The credit for anything good you find here goes to the home-assistant team.
    const root = this.cols;
    // Remove old columns
    while (root.lastChild) {
      root.removeChild(root.lastChild);
    }

    // Prepare a number of new columns
    let columns = [];
    const columnEntityCount =  [];
    for(let i = 0; i < this.columns; i++) {
      columns.push([]);
      columnEntityCount.push(0);
    }

    function getColumnIndex(size) {
      // Find the shortest column
      let minIndex = 0;
      for (let i = 0; i < columnEntityCount.length; i++) {
        if (columnEntityCount[i] < 5) {
          minIndex = i;
          break;
        }
        if (columnEntityCount[i] < columnEntityCount[minIndex]) {
          minIndex = i;
        }
      }
      columnEntityCount[minIndex] += size;
      return minIndex;
    }

    // Go through each card and find which column to place it in (the shortest one)
    this._cards.forEach((el) => {
      this.appendChild(el);
      const cardSize = typeof el.getCardSize === 'function' ? el.getCardSize() : 1;
      columns[getColumnIndex(cardSize)].push(el);
    });

    this.columnEntityCount = columnEntityCount

    // Remove any empty columns
    columns = columns.filter(val => val.length > 0);

    // Actually place the cards in the columns
    columns.forEach((column) => {
      const columnEl = document.createElement('div');
      columnEl.classList.add('column');
      column.forEach(el => columnEl.appendChild(el));
      root.appendChild(columnEl);
    });
    
    const column = this.shadowRoot.querySelector('.column');

    if (this.config.column_style) {
      Object.keys(this.config.column_style).forEach((prop) => {
        column.style.setProperty(prop, this.config.column_style[prop]);
      });
    }
  }

  set hass(hass) {
    // console.log(hass);
    this._cards.forEach(item => {
      item.hass = hass;
    });
  }

  getCardSize() {
    return 1;
    return Math.max(this.columnEntityCount);
  }
}
customElements.define('horizontal-scroll-card', HorizontalScrollCard);