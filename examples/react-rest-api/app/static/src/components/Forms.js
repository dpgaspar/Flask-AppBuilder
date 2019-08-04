import React, { Component } from 'react';
import { Modal, Button } from 'react-bootstrap';
import Select from 'react-select';

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


export class FormFieldFilter extends Component {
  render() {
    return (
      <table class="table table-responsive table-hover filters">
        <tbody>
          <tr>
            <td class="col-lg-1 col-md-1">
              <a onClick={this.props.onClick} href="#" class="btn remove-filter">
                <span class="close-icon">×</span>&nbsp;{this.props.label}
              </a>
            </td>
            <td>
              <input
                onChange={this.props.onChange}
                class="form-control"
                id={this.props.name}
                name={this.props.name}
                placeholder={this.props.label}
                type="text"
              />              
            </td>
          </tr>
        </tbody>
      </table>
    );
  }
}


export class FormField extends Component {

  constructor(props) {
    super(props);
  }
  
  convertOptions() {
    let options = []; 
    for (let i in this.props.options) {
      options.push({label: this.props.options[i].value, value: this.props.options[i].id});
    }
    return options;
  }

  dynamicField() {
    if (this.props.type == "Related") {
      return (
      <Select
        id={this.props.name}
        name={this.props.name}
        required={this.props.required}
        options={this.convertOptions()}
      />);
    }
    else {
      return (
      <input
          onChange={this.props.onChange}
          class="form-control"
          id={this.props.name}
          name={this.props.name}
          placeholder={this.props.label}
          required={this.props.required}
          type="text"
        />);
    }
  }

  render() {
    return (
      <div class="form-group">
        <label
          class="col-form-label"
          for={this.props.name}
        >
          {this.props.label}:
        </label>
        {this.dynamicField()}     
      </div>
    );
  }
}


export class AddForm extends Component {

  constructor(props) {
    super(props);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  form() {
    return this.props.info.addColumns.map(function (object, i) {
      return <FormField
        name={object.name}
        label={object.label}
        required={object.required}
        type={object.type}
        options={object.values}
      />;
    }, this);
  }

  handleSubmit(event) {
    event.preventDefault();
    let formObject = {};
    console.dir(event.target.elements);
    for (let i in event.target.elements) {
      if (event.target.elements[i].nodeName == 'INPUT' && event.target.elements[i].name != '') {
        formObject[event.target.elements[i].name] = event.target.elements[i].value;
      }
    }
    this.props.onAdd(formObject);
  }

  render() {
    return (
      <Modal show={this.props.show} onHide={this.props.onClose}>
        <Modal.Header closeButton>
          <Modal.Title>
            {this.props.info.addTitle}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form onSubmit={this.handleSubmit}>
            {this.form()}
          <Button onClick={this.props.onClose}>Close</Button>
          <Button bsStyle="primary" type="submit">Save</Button>
          </form>          
        </Modal.Body>

      </Modal>
    )
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
