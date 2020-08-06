
class filterList {
  /**
   * Build a filter list for a field
   * @param {HTMLElement} parent Parent HTML object
   * @param {object} values Values for filtering
   * @param {function} callback Function to call when filtering is changed
   * @param {string|null} initial Initial filtering value, set to null for no filtering
   */
  constructor (parent, values, callback, initial = null) {
    this.list = document.createElement('ul')
    parent.appendChild(this.list)
    this.callback = callback

    this.li_all = document.createElement('li')
    this.li_all.textContent = 'Alle'
    this.li_all.addEventListener('click', () => { this.removeFilter() })
    this.list.appendChild(this.li_all)
    this.removeFilter()

    for (const value of values) {
      const li = document.createElement('li')
      li.textContent = value
      li.addEventListener('click', (event) => { this.setFilter(event.target) })
      this.list.appendChild(li)
      if (value === initial) {
        this.setFilter(li)
      }
    }
  }

  /**
   * Set filtering value
   * @param {HTMLElement|EventTarget} element <li> element
   */
  setFilter (element) {
    this.selected.removeAttribute('class')
    element.setAttribute('class', 'selected')
    this.selected = element
    this.selected_value = element.textContent
    this.callback()
  }

  /**
   * Remove filtering and show all values
   */
  removeFilter () {
    if (this.selected) {
      this.selected.removeAttribute('class')
    }
    this.li_all.setAttribute('class', 'selected')
    this.selected = this.li_all
    this.selected_value = null
    this.callback()
  }
}

class filterGroup {
  /**
   * Add a filtering group
   * @param {string} parentElementId Id of parent element to add the filtering group to
   */
  constructor (parentElementId) {
    this.parentElement = document.getElementById(parentElementId)
    this.filters = {}
    this.params = new URLSearchParams(window.location.search)
  }

  /**
   * Add a filter list
   * @param {string} field Field name
   * @param {object} values Filter values
   * @param {string} header Header text for the filter list
   */
  addFilter (field, values, header) {
    const h3 = document.createElement('h3')
    h3.textContent = header
    this.parentElement.appendChild(h3)

    this.filters[field] = new filterList(this.parentElement, values, () => { this.setFilterParams() }, this.params.get(field))
  }

  /**
   * Add a filter list using JSON data from an object named "[field name]-data"
   * @param {string} field Field name
   * @param {string} header Header text for the filter list
   */
  addFilterJson (field, header) {
    const values = JSON.parse(document.getElementById(field + '-data').textContent)
    this.addFilter(field, values, header)
  }

  /**
   * Set GET parameters for filtering
   */
  setFilterParams () {
    for (const field in this.filters) {
      console.log(field, this.filters[field].selected_value)
      const value = this.filters[field].selected_value
      console.log(value)
      if (value !== null && value !== '') {
        this.params.set(field, value)
      } else {
        this.params.delete(field)
      }
    }

    const queryString = '?' + this.params.toString()

    let currentQueryString
    if (window.location.search === '') { currentQueryString = '?' } else { currentQueryString = window.location.search }
    console.log(currentQueryString)
    console.log(queryString)
    if (currentQueryString !== queryString) { window.location.replace(queryString) }
  }
}
