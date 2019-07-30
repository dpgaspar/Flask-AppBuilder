import React, { Component } from 'react';
import { AddButton, CRUDRowButtons, DeleteModal } from './CRUDButtons';
import { AddForm, ShowForm } from './Forms';
import Api from '../api/Api';

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
      <thead><tr><th></th>{row}</tr></thead>
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

class Table extends Component {

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
      currentId: null,
      currentItem: null,
      count: 0,
      ids: [],
      data: [],
      listColumns: [],
      labelColumns: [],
      orderByCol: '-',
      orderByDir: '-'
    };
    this.onOrderBy = this.onOrderBy.bind(this);
    this.onOpenShowForm = this.onOpenShowForm.bind(this);
    this.onCloseShowForm = this.onCloseShowForm.bind(this);
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

  onAdd() {
    alert('add');
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

  refresh() {
    this.api.get(this.props.resource, [], this.prepareOrder())
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

  rows() {
    const listColumns = this.state.listColumns
    return this.state.data.map(function (object, i) {
      return <TableRow
        resource={this.props.resource}
        listColumns={listColumns}
        obj={object}
        id={this.state.ids[i]}
        setCurrentId={this.setCurrentId}
        onOpenShowForm={this.onOpenShowForm}
      />;
    }, this);
  }

  render() {
    return (
      <div>
        <div class="well well-sm">
          <AddButton resource={this.props.resource} modalId="add-modal" />
          <TableRecordCount count={this.state.count} />
        </div>
        <div class="table-responsive">
          <table className="table table-bordered table-hover">
            <TableHeader
              listColumns={this.state.listColumns}
              labelColumns={this.state.labelColumns}
              orderByCol={this.state.orderByCol}
              orderByDir={this.state.orderByDir}
              onOrderBy={this.onOrderBy}
            />
            <tbody>
              {this.rows()}
            </tbody>
          </table>
        </div>
        <DeleteModal
          modalId='delete-modal'
          resource={this.props.resource}
          onOk={this.onDelete}
          id={this.state.currentId}
        />
        <AddForm
          modalId='add-modal'
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

export default Table;
