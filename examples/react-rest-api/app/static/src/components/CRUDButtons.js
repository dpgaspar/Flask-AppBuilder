import React, { Component } from 'react';
import { Button } from 'react-bootstrap';

export class AddButton extends Component {
  constructor(props) {
    super(props);
    this.onClick = this.onClick.bind(this);
  }

  onClick() {
    this.props.onOpenAddForm();
  }

  render() {
    return (
      <Button bsStyle="primary" bsSize="sm" onClick={this.onClick}>
      <i class="fa fa-plus"></i>
      </Button>
    );
  }
}

export class EditButton extends Component {

  render() {
    return (
      <a
        href={this.props.resource + "/edit/" + this.props.id}
        class="btn btn-sm btn-default"
        data-toggle="tooltip"
        rel="tooltip"
        title=""
        data-original-title="Edit record"
      >
        <i class="fa fa-edit"></i>
      </a>
    );
  }
}

export class DeleteModal extends Component {

  render() {
    return (
      <div class="modal fade" id={this.props.modalId} tabindex="-1" role="dialog">
        <div class="modal-dialog modal-sm">
          <div class="modal-content">
            <div class="modal-header">
              <h4 class="modal-title" id="myModalLabel">
                User confirmation needed
              </h4>
            </div>
            <div class="modal-body">
              <div class="modal-text">
                Do you want to delete the {this.props.resource} record {this.props.id}
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
              <button type="button" onClick={this.props.onOk} class="btn btn-danger" data-dismiss="modal">OK</button>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export class DeleteButton extends Component {

  constructor(props) {
    super(props);
    this.onClick = this.onClick.bind(this);
  }

  onClick() {
    this.props.setCurrentId(this.props.id);
  }

  render() {
    return (
      <a
        class="btn btn-sm btn-default confirm"
        rel="tooltip"
        href="#"
        data-toggle="modal"
        onClick={this.onClick}
        data-target={"#" + this.props.modalId}
      >
        <i class="fa fa-trash"></i>
      </a>
    );
  }
}

export class ShowButton extends Component {
  constructor(props) {
    super(props);
    this.onClick = this.onClick.bind(this);
  }

  onClick() {
    this.props.onOpenShowForm(this.props.id);
  }

  render() {
    return (
      <a
        class="btn btn-sm btn-default confirm"
        rel="tooltip"
        href="#"
        data-toggle="modal"
        onClick={this.onClick}
        data-original-title="Show record"
      >
        <i class="fa fa-search"></i>
      </a>
    );
  }
}

export class CRUDRowButtons extends Component {

  render() {
    const showButton =
      <ShowButton
        resource={this.props.resource}
        id={this.props.id}
        modalId="show-modal"
        setCurrentId={this.props.setCurrentId}
        onOpenShowForm={this.props.onOpenShowForm}
        />
    const editButton = <EditButton resource={this.props.resource} id={this.props.id} />
    const deleteButton =
      <DeleteButton
        resource={this.props.resource}
        id={this.props.id}
        modalId="delete-modal"
        setCurrentId={this.props.setCurrentId}
      />
    return (
      <td class="col-md-1 col-lg-1 col-sm-1">
        <center>
          <div class="btn-group btn-group-xs" style={{ display: 'flex' }}>
            {showButton}
            {editButton}
            {deleteButton}
          </div>
        </center>
      </td>
    );
  }
}
