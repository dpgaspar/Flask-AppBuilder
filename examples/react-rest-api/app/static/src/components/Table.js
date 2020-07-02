import React, { Component } from 'react';
import { AddButton, CRUDRowButtons, DeleteModal } from './CRUDButtons';
import { AddForm, ShowForm, FormFieldFilter } from './Forms';
import {
  Panel,
  DropdownButton,
  MenuItem,
  Pagination,
  ButtonToolbar,
  ButtonGroup,
  Button
} from 'react-bootstrap';
import Api from '../api/Api';


class TableFilters extends Component {
  constructor(props) {
    super(props);
    this.onAddFilter = this.onAddFilter.bind(this);
    this.onChangeFilter = this.onChangeFilter.bind(this);
    this.onRemoveFilter = this.onRemoveFilter.bind(this);
  }

  filterItems() {
    let items = []
    for (let item in this.props.filters) {
      items.push(
        <MenuItem onClick={() => this.onAddFilter(item)} eventKey="{item}">{item}</MenuItem>
      );
    }
    return items;
  }

  currentFilterItems() {
    let items = []
    for (let item in this.props.currentFilters) {
      items.push(
          <FormFieldFilter
            onChange={this.onChangeFilter}
            onClick={() => this.onRemoveFilter(this.props.currentFilters[item].col)}
            name={this.props.currentFilters[item].col}
            label={this.props.currentFilters[item].col}
          />
      );
    }
    return items;
  }

  onChangeFilter(e) {
    this.props.onChangeFilter(e.target.id, 'sw', e.target.value);
  }

  onAddFilter(colName) {
    this.props.onAddFilter(colName, 'sw', '');
  }

  onRemoveFilter(colName) {
    this.props.onRemoveFilter(colName);
  }

  render() {
    return (
      <Panel bsStyle="success" id="collapsible-panel-example-2">
        <Panel.Heading>
          <Panel.Title toggle>Filters</Panel.Title>
        </Panel.Heading>
        <Panel.Body collapsible>
          <DropdownButton
            title="Add Filter"
          >
            {this.filterItems()}
          </DropdownButton>
          {this.currentFilterItems()}
        </Panel.Body>
      </Panel>
    );
  }
}

class TablePagination extends Component {
  constructor(props) {
    super(props);
    this.state = {
      currentPage: 0
    };
    this.onFirst = this.onFirst.bind(this);
    this.onNext = this.onNext.bind(this);
    this.onPrev = this.onPrev.bind(this);
    this.onLast = this.onLast.bind(this);
    this.onPageSize = this.onPageSize.bind(this);
  }

  onClick(page) {
    this.setState({ currentPage: page });
    this.props.onChangePage(page);
  }

  onPageSize(pageSize) {
    this.props.onChangePageSize(pageSize);
  }

  onFirst() {
    this.setState({ currentPage: 0 });
    this.props.onChangePage(0);
  }

  onLast() {
    this.setState({ currentPage: Math.floor(this.props.count / this.props.pageSize) });
    this.props.onChangePage(Math.floor(this.props.count / this.props.pageSize));
  }

  onPrev() {
    let page = this.state.currentPage;
    if (page != 0) {
      this.setState({ currentPage: page - 1 });
    }
    this.props.onChangePage(page - 1);
  }

  onNext() {
    let page = this.state.currentPage;
    if (page != Math.floor(this.props.count / this.props.pageSize)) {
      this.setState({ currentPage: page + 1 });
      this.props.onChangePage(page + 1);
    }
  }

  pageItems() {
    let items = [];
    let actualNumPages = Math.floor(this.props.count / this.props.pageSize);
    let maxNumPages = 10;
    let numPages = 10;
    let firstPage = 0;
    if (maxNumPages > actualNumPages) {
      numPages = actualNumPages;
    }
    if ((actualNumPages - this.state.currentPage) <= (numPages / 2)) {
      firstPage = actualNumPages - numPages;
      numPages = actualNumPages;
    }
    else if (this.state.currentPage > (numPages / 2)) {
      firstPage = this.state.currentPage - (numPages / 2);
      numPages = numPages + this.state.currentPage - (numPages / 2);
    }

    for (let number = firstPage; number <= (numPages); number++) {
      items.push(
        <Pagination.Item
          onClick={() => this.onClick(number)}
          key={number}
          active={number === this.state.currentPage}
        >
          {number}
        </Pagination.Item>,
      );
    }
    return items;
  }

  pageSizeItems() {
    let items = [];
    let pageSizes = [10, 20, 50, 100];
    for (let i in pageSizes) {
      if (this.props.pageSize == pageSizes[i]) {
        items.push(
          <MenuItem
            eventKey="1"
            onClick={() => this.onPageSize(pageSizes[i])}
            active
          >
            {pageSizes[i]}
          </MenuItem>
        )
      }
      else {
        items.push(
          <MenuItem
            eventKey="1"
            onClick={() => this.onPageSize(pageSizes[i])}
          >
            {pageSizes[i]}
          </MenuItem>
        )
      }
    }
    return items;
  }

  render() {
    if (this.props.count > this.props.size) {
      return (
        <div>
          <Pagination bsSize="small" style={{ margin: 0 }}>
            <Pagination.First onClick={this.onFirst} />
            <Pagination.Prev onClick={this.onPrev} />
            {this.pageItems()}
            <Pagination.Next onClick={this.onNext} />
            <Pagination.Last onClick={this.onLast} />
          </Pagination>
          <DropdownButton
            bsSize="small"
            title="Page size"
            style={{ margin: 0 }}
          >
            {this.pageSizeItems()}
          </DropdownButton>
        </div>
      );
    }
    return ('');
  }
}

class TableRecordCount extends Component {

  render() {
    return (
      <div class="pull-right">
        <strong>Record Count:</strong> {this.props.count}
      </div>
    );
  }
}

class TableHeader extends Component {

  constructor(props) {
    super(props);
  }

  getOrderbyArrow(column) {
    var orderBy = 'asc';
    if (this.props.orderByCol == column) {
      orderBy = this.props.orderByDir;
    }
    else {
      return (<i class="fa fa-arrows-v pull-right"></i>);
    }
    if (orderBy == 'asc') {
      return (<i class="fa fa-arrow-up pull-right"></i>);
    }
    else {
      return (<i class="fa fa-arrow-down pull-right"></i>);
    }
  }

  render() {
    const row = this.props.listColumns.map(
      key =>
        <th>
          <a
            href="#"
            onClick={() => this.props.onOrderBy(key)}
          >
            {this.props.labelColumns[key]}{this.getOrderbyArrow(key)}
          </a>
        </th>
    )
    return (
      <thead><tr><th>#</th>{row}</tr></thead>
    );
  }
}

class TableRow extends Component {

  render() {
    const row = this.props.listColumns.map(key => <td>{this.props.obj[key]}</td>)
    const crudRowButtons =
      <CRUDRowButtons
        resource={this.props.resource}
        id={this.props.id}
        setCurrentId={this.props.setCurrentId}
        onOpenShowForm={this.props.onOpenShowForm}
      />
    return (
      <tr key={this.props.key}>
        {crudRowButtons}
        {row}
      </tr>
    );
  }
}


class CRUDTable extends Component {

  constructor(props) {
    super(props);
    this.api = new Api();
    this.info = {
      addTitle: '',
      editTitle: '',
      addColumns: [],
      editColumns: [],
      filters: {},
      permissions: []
    }
    this.state = {
      showShowForm: false,
      showAddForm: false,
      currentId: null,
      currentItem: null,
      currentFilters: [],
      count: 0,
      ids: [],
      page: 0,
      pageSize: 20,
      data: [],
      listColumns: [],
      labelColumns: [],
      orderByCol: '-',
      orderByDir: '-'
    };
    this.onOrderBy = this.onOrderBy.bind(this);
    this.onChangePage = this.onChangePage.bind(this);
    this.onChangePageSize = this.onChangePageSize.bind(this);
    this.onAddFilter = this.onAddFilter.bind(this);
    this.onRemoveFilter = this.onRemoveFilter.bind(this);
    this.onChangeFilter = this.onChangeFilter.bind(this);
    this.onOpenShowForm = this.onOpenShowForm.bind(this);
    this.onCloseShowForm = this.onCloseShowForm.bind(this);
    this.onOpenAddForm = this.onOpenAddForm.bind(this);
    this.onCloseAddForm = this.onCloseAddForm.bind(this);
    this.onAdd = this.onAdd.bind(this);
    this.onDelete = this.onDelete.bind(this);
    this.setCurrentId = this.setCurrentId.bind(this);
  }

  setCurrentId(id) {
    this.setState(
      {
        currentId: id
      });
  }

  onOpenShowForm(id) {
    this.getItem(id);
    this.setState(
      {
        currentId: id,
        showShowForm: true
      });
  }

  onCloseShowForm() {
    this.setState(
      {
        showShowForm: false
      });
  }

  onChangeFilter(colName, opr = "sw", value) {
    let currentFilters = [...this.state.currentFilters];
    for (let key in this.info.filters) {
      if (key == colName) {
        for (let i in currentFilters) {
          if (currentFilters[i].col == colName) {
            currentFilters[i] = { col: colName, opr: opr, value: value };    
          }
        }
      }
    }
    this.setState(
      {
        currentFilters: currentFilters
      }, () => this.refresh());
  }


  onAddFilter(colName, opr = "sw", value = "") {
    let currentFilters = [...this.state.currentFilters];
    for (let key in this.info.filters) {
      if (key == colName) {
        currentFilters.push({ col: colName, opr: opr, value: value });
      }
    }
    this.setState(
      {
        currentFilters: currentFilters
      }, () => this.refresh());
  }

  onRemoveFilter(colName, opr = "sw", value = "") {
    let currentFilters = [];
    for (let item in this.state.currentFilters) {
      if (this.state.currentFilters[item].col != colName)
        currentFilters.push(this.state.currentFilters[item]);
    }
    this.setState(
      {
        currentFilters: currentFilters
      }, () => this.refresh());
  }

  onOpenAddForm(id) {
    this.setState(
      {
        showAddForm: true
      });
  }

  onCloseAddForm() {
    this.setState(
      {
        showAddForm: false
      });
  }

  onAdd(data) {
    this.api.post(this.props.resource, data)
      .then(response => {
        this.refresh();
      })
      .catch(function (error) {
        alert(JSON.stringify(error.response.data, null, 4));
      })
      this.onCloseAddForm();
  }

  onDelete(id) {
    this.api.delete(this.props.resource, this.state.currentId)
      .then(response => {
        this.refresh();
      })
      .catch(function (error) {
        console.log(error);
      })
  }

  onOrderBy(column) {
    var newOrder = 'asc';
    if (this.state.orderByDir == 'asc') {
      newOrder = 'desc';
    }
    this.setState(
      {
        orderByCol: column,
        orderByDir: newOrder
      }, () => this.refresh());
  }

  onChangePage(page) {
    this.setState(
      {
        page: page
      }, () => this.refresh());
  }

  onChangePageSize(pageSize) {
    this.setState(
      {
        pageSize: pageSize
      }, () => this.refresh());
  }

  flattenObject(obj, dst = {}, prefix = '') {
    Object.entries(obj).forEach(([key, val]) => {
      if (val && typeof val == 'object') this.flattenObject(val, dst, prefix + key + '.');
      else dst[prefix + key] = val;
    });
    return dst;
  }

  flattenList(lst) {
    var ret = [];
    var item = {};
    lst.forEach(function (item) {
      var fItem = this.flattenObject(item);
      ret.push(fItem);
    }, this);
    return ret;
  }

  prepareOrder() {
    var order = {};
    if (this.state.orderByCol != '-') {
      order = {
        column: this.state.orderByCol,
        direction: this.state.orderByDir
      };
    }
    return order;
  }

  componentDidMount() {
    this.getInfo();
    this.refresh();
  }

  getInfo() {
    this.api.info(this.props.resource)
      .then(response => {
        this.info.addTitle = response.data.add_title;
        this.info.addColumns = response.data.add_columns;
        this.info.editTitle = response.data.edit_title;
        this.info.filters = response.data.filters;
        this.info.permissions = response.data.permissions;
      })
      .catch(function (error) {
        console.log(error);
      })
  }

  getRequestParameters() {
    return {
      ...(this.state.currentFilters != []) && {filters: this.state.currentFilters},
      ...(this.state.orderByCol != '-') && { order_column: this.state.orderByCol },
      ...(this.state.orderByDir != '-') && { order_direction: this.state.orderByDir },
      page: this.state.page,
      page_size: this.state.pageSize
    }
  }

  refresh() {
    this.api.get(this.props.resource, this.getRequestParameters())
      .then(response => {
        this.setState(
          {
            count: response.data.count,
            ids: response.data.ids,
            data: this.flattenList(response.data.result),
            listColumns: response.data.list_columns,
            labelColumns: response.data.label_columns
          });
      })
      .catch(function (error) {
        console.log(error);
      })
  }

  getItem(id) {
    this.api.getItem(this.props.resource, id)
      .then(response => {
        this.setState(
          {
            currentItem: {
              title: response.data.show_title,
              label_columns: response.data.label_columns,
              result: this.flattenObject(response.data.result)
            }
          });
      })
      .catch(function (error) {
        console.log(error);
      })
  }

  tableRows() {
    const listColumns = this.state.listColumns
    return this.state.data.map(function (object, i) {
      return <TableRow
        resource={this.props.resource}
        listColumns={listColumns}
        obj={object}
        id={this.state.ids[i]}
        setCurrentId={this.setCurrentId}
        onOpenShowForm={this.onOpenShowForm}
        onOpenAddForm={this.onOpenAddForm}
      />;
    }, this);
  }

  tableControl() {
    return (
      <Panel>
      <Panel.Body>
        <ButtonToolbar>
          <ButtonGroup>
            <AddButton
              resource={this.props.resource}
              onOpenAddForm={this.onOpenAddForm}
            />
          </ButtonGroup>
          <ButtonGroup>
            <TablePagination
              onChangePage={this.onChangePage}
              onChangePageSize={this.onChangePageSize}
              size={this.state.ids.length}
              count={this.state.count}
              pageSize={this.state.pageSize}
            />
          </ButtonGroup>
          <TableRecordCount count={this.state.count} />
        </ButtonToolbar>
      </Panel.Body>
    </Panel>
    );
  }

  tableContent() {
    return(
      <div class="table-responsive">
          <table className="table table-hover">
            <TableHeader
              listColumns={this.state.listColumns}
              labelColumns={this.state.labelColumns}
              orderByCol={this.state.orderByCol}
              orderByDir={this.state.orderByDir}
              onOrderBy={this.onOrderBy}
            />
            <tbody>
              {this.tableRows()}
            </tbody>
          </table>
        </div>
    );
  }

  render() {
    return (
      <div>
        <TableFilters
          filters={this.info.filters}
          currentFilters={this.state.currentFilters}
          onChangeFilter={this.onChangeFilter}
          onAddFilter={this.onAddFilter}
          onRemoveFilter={this.onRemoveFilter}
        />
        {this.tableControl()}
        {this.tableContent()}
        <DeleteModal
          modalId='delete-modal'
          resource={this.props.resource}
          onOk={this.onDelete}
          id={this.state.currentId}
        />
        <AddForm
          show={this.state.showAddForm}
          onOpen={this.onOpenAddForm}
          onClose={this.onCloseAddForm}
          onAdd={this.onAdd}
          info={this.info}
        />
        <ShowForm
          resource={this.props.resource}
          show={this.state.showShowForm}
          onOpen={this.onOpenShowForm}
          onClose={this.onCloseShowForm}
          id={this.state.currentId}
          item={this.state.currentItem}
        />
      </div>
    );
  }
}

export default CRUDTable;
