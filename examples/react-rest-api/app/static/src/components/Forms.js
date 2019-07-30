import React, { Component } from 'react';
import { Modal, Button } from 'react-bootstrap';


class ShowField extends Component {
  render() {
    return (
      <tr>
        <td><b>{this.props.label}</b></td>
        <td>{this.props.value}</td>
      </tr>
    );
  }
}

class FormField extends Component {
  render() {
    return (
      <div class="form-group">
        <label
          class="col-form-label"
          for={this.props.name}
        >
          {this.props.label}:
        </label>
        <input
          class="form-control"
          id={this.props.name}
          name={this.props.name}
          placeholder={this.props.label}
          required
          type="text"
        />
      </div>
    );
  }
}


export class AddForm extends Component {

  constructor(props) {
    super(props);
  }

  form() {
    return this.props.info.addColumns.map(function (object, i) {
      return <FormField
        name={object.name}
        label={object.label}
      />;
    }, this);
  }

  render() {
    return (
      <div class="modal fade" id={this.props.modalId} tabindex="-1" role="dialog">
        <div class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header">
              <h4 class="modal-title" id="myModalLabel">
                {this.props.info.addTitle}
              </h4>
            </div>
            <div class="modal-body">
              <form>
                {this.form()}
              </form>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
              <button type="button" onClick={this.props.onAdd} class="btn btn-primary" data-dismiss="modal">Save</button>
            </div>
          </div>
        </div>
      </div>
    );
  }
}


export class ShowForm extends React.Component {

  form() {
    return Object.keys(this.props.item.result).map(function (key) {
      return <ShowField
        label={this.props.item.label_columns[key]}
        value={this.props.item.result[key]}
      />;
    }, this)
  }

  render() {
    return (
      <Modal show={this.props.show} onHide={this.props.onClose}>
        <Modal.Header closeButton>
          <Modal.Title>
            {this.props.item ? this.props.item.title : 'NoTitle'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <table className="table table-hover">
            <tbody class="table">
              {this.props.item ? this.form() : 'NO DATA'}
            </tbody>
          </table>
        </Modal.Body>

        <Modal.Footer>
          <Button onClick={this.props.onClose}>Close</Button>
        </Modal.Footer>
      </Modal>
    )
  }
}

export default AddForm;
