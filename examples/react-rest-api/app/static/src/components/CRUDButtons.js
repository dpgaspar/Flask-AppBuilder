import React, { Component } from 'react';


export class AddButtom extends Component {

    constructor(props) {
        super(props);
    }

    render () {
        return (
            <a
                href={this.props.resource + "/add"}
                class="btn btn-sm btn-primary"
                data-toggle="tooltip"
                rel="tooltip"
                title=""
                data-original-title="Add a new record"
            >
                <i class="fa fa-plus"></i>
            </a>
        );
    }
}

export class EditButtom extends Component {

    constructor(props) {
        super(props);
    }

    render () {
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

export class DeleteButtom extends Component {

    constructor(props) {
        super(props);
    }

    render () {
        return (
            <a
                data-text="You sure you want to delete this item?"
                href={this.props.resource + "/edit/" + this.props.id}
                class="btn btn-sm btn-default confirm"
                rel="tooltip" title=""
                data-toggle="modal"
                data-target="#modal-confirm"
                href="#"
                data-original-title="Delete record"
            >
                <i class="fa fa-eraser"></i>
            </a>
        );
    }
}
