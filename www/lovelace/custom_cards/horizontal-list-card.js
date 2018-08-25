class HorizontalListCard extends HTMLElement {

    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
    }

    setConfig(config) {
      if (!config.entity || !config.image_field || !config.separator_field || !config.primary_right_text_field || !config.secondary_text_field) {
        throw new Error('Please define an entity');
      }

      const root = this.shadowRoot;
      if (root.lastChild) root.removeChild(root.lastChild);

      const cardConfig = Object.assign({}, config);
      if (!cardConfig.title) cardConfig.title = 'List';

      const card = document.createElement('ha-card');
      const content = document.createElement('div');
      const style = document.createElement('style');
      // const icon = document.createElement('ha-icon');
      // icon.src = 'mdi:calendar';
      style.textContent = `
            ha-card {
              position: relative;
              ${cardConfig.style}
            }
            ha-icon {
              float: left;
              margin-left: 30px;
              margin-top: 30px;
            }
            table {
              width: 100%;
              padding: 0 32px 0 32px;
            }
            td, th {
              max-width: 200px;
              text-align: left;
              vertical-align: top;
            }
            
            .title {
              color: red;
            }
            .primary {
              
            }
            .secondary {
              font-size: 0.8em;
            }
            col {
              width: 200px;
            }
          `;

      content.id = "container";
      // card.appendChild(icon);
      card.header = cardConfig.title;
      card.appendChild(content);
      card.appendChild(style);
      root.appendChild(card);
      this._config = cardConfig;
    }
    
    applyTemplate(item, field, regex) {
      let displayText = item[field];

      if (regex) {
        displayText =  new RegExp(regex).exec(item[field])[0];
      }
      
      return displayText;
    }

    set hass(hass) {
      const root = this.shadowRoot;
      const card = root.lastChild;
      const entity = this._config.entity;
      const list_attribute = this._config.list_attribute;
      const column_limit = this._config.column_limit ? this._config.column_limit : 5;
      const show_image_count = this._config.show_image_count ? this._config.show_image_count : 2;
      const image_field = this._config.image_field;
      const separator_field = this._config.separator_field;
      const title_field = this._config.title_field;
      const primary_left_text_field = this._config.primary_left_text_field;
      const primary_right_text_field = this._config.primary_right_text_field;
      const secondary_text_field = this._config.secondary_text_field;
      const separator_regex = this._config.separator_regex;
      const title_regex = this._config.title_regex;
      const primary_left_text_regex = this._config.primary_left_text_regex;
      const primary_right_text_regex = this._config.primary_right_text_regex;
      const secondary_text_regex = this._config.secondary_text_regex;

      if (hass.states[entity]) {
        const list = hass.states[entity].attributes;
        this.style.display = 'block';
        let column_count = 0;

        if (list !== undefined && Object.keys(list).length > 0) {
          
          let display_list = {};
          for (const [key, item] of Object.entries(list)) {
            if (!item.hasOwnProperty(separator_field)) continue;
            let separator = this.applyTemplate(item, separator_field, separator_regex); // TODO why isn't separator coming back right?
                      
            if (!display_list.hasOwnProperty(separator)) {
              display_list[separator] = [];
            }
            
            const re = /"(.*?)"/g;
            let right = re.exec(item[primary_right_text_field]);

            display_list[separator].push({
              "image": item[image_field][0].url, // TODO Be able to support non-url
              "title": this.applyTemplate(item, title_field, title_regex),
              "primary_left": this.applyTemplate(item, primary_left_text_field, primary_left_text_regex),
              "primary_right": right !== null ? right[0] : '',
              "secondary": this.applyTemplate(item, secondary_text_field, secondary_text_regex)
            });
          }
          
          let card_content = '<table><thread><tr>';
          let card_column_content = '';
          let card_header_content = '';
          let card_data_content = '';
            
          for (const [header, entry] of Object.entries(display_list)) {
            if (column_count >= column_limit) break;
            
            card_column_content += `<col>`;
            card_header_content += `<td>${header}</td>`;
            
            if (column_count < show_image_count) {
              card_column_content += `<col>`;
              card_header_content += `<td></td>`;
            }
            
            card_data_content += `<td>`;
            
            
            
            let first_rendered = false;

            for (const [field_name, field] of Object.entries(entry)) {
              if (first_rendered) {
                card_data_content += `<hr>`;
              }
              
              card_data_content += `<div>`; // TODO Wrap in a <div>?
              
              // TODO Image should be in it's column
              if (column_count < show_image_count && field.image !== "" && !first_rendered) {
                card_data_content += `<img class="image" src="${field.image}" width="200">`;
                card_data_content += `</div></td><td><div>`;
              }
              
              if (!first_rendered) {
                first_rendered = true;
              }
                
              card_data_content += `<span class="title">${field.title}</span><br>`;
              card_data_content += `<span class="primary">${field.primary_left}&nbsp${field.primary_right}</span><br>`;
              card_data_content += `<span class="secondary">${field.secondary}</span><br>`;
              card_data_content += `</div>`;
            }
            
            card_data_content += `</td>`;
            column_count++;
          }
          
          card_header_content += `</tr></thead><tbody><tr>`;
          card_data_content += `</tr></tbody></table>`;
          card_content += card_column_content + card_header_content + card_data_content;
          root.lastChild.hass = hass;
          root.getElementById('container').innerHTML = card_content;
        } else {
          this.style.display = 'none';
        }
      } else {
        this.style.display = 'none';
      }
    }

    getCardSize() {
      return 1;
    }
  }

  customElements.define('horizontal-list-card', HorizontalListCard);