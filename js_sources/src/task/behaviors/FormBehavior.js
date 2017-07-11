/*
 * File Name : FormBehavior.js
 *
 * Copyright (C) 2012 Gaston TJEBBES g.t@majerti.fr
 * Company : Majerti ( http://www.majerti.fr )
 *
 * This software is distributed under GPLV3
 * License: http://www.gnu.org/licenses/gpl-3.0.txt
 *
 */
import Mn from 'backbone.marionette';
import Validation from 'backbone-validation';
import { serializeForm } from '../../tools.js';
import {BootstrapOnInvalidForm, BootstrapOnValidForm, displayServerError, displayServerSuccess} from '../../backbone-tools.js';

var FormBehavior = Mn.Behavior.extend({
	ui: {
        form: "form",
        submit: "button[type=submit]"
    },
    events: {
        'click @ui.submit': 'onSubmitForm'
    },
    defaults: {
        errorMessage: "Une erreur est survenue"
    },
    serializeForm: function(){
        return serializeForm(this.getUI('form'));
    },
    onRender: function() {
        //Set up any other form related stuff here
        Validation.unbind(this.view);
        Validation.bind(this.view);
    },
    onSyncError: function(){
        displayServerError("Une erreur a été rencontrée lors de la " +
                           "sauvegarde de vos données");
    },
    onSyncSuccess: function(){
        displayServerSuccess("Vos données ont bien été sauvegardées");
    },
    syncServer: function(){
        if (this.view.model.isValid()){
            this.view.model.save(
                this.view.model.toJSON(),
                {
                    success: this.onSyncSuccess.bind(this),
                    error: this.onSyncError.bind(this),
                }
            );
        }
    },
    onSubmitForm: function(){
        this.view.model.set(this.serializeForm(), {validate: true});
        this.syncServer();
    },
    onDataModified: function(view, attribute, value){
        console.log("Data modified");
        const error = this.view.model.preValidate(attribute, value);

        if (error){
            BootstrapOnInvalidForm(view, attribute, error, 'name');
        } else {
            BootstrapOnValidForm(view, attribute, 'name');
        }
    }
});

export default FormBehavior;
