odoo.define('mobile_android.ajax', function (require) {
    var Session = require('web.Session');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var utils = require('web.utils');
    var time = require('web.time');
    var download = require('web.download');
    var contentdisposition = require('web.contentdisposition');
    ajax.get_file = function(options) {
        var xhr = new XMLHttpRequest();
        var data;
        if (options.form) {
            xhr.open(options.form.method, options.form.action);
            data = new FormData(options.form);
        } else {
            xhr.open('POST', options.url);
            data = new FormData();
            _.each(options.data || {}, function(v, k) {
                data.append(k, v)
            });
        }
        data.append('token', 'dummy-because-api-expects-one');
        if (core.csrf_token) {
            data.append('csrf_token', core.csrf_token);
        }
        xhr.responseType = 'blob';
        xhr.onload = function() {
            var mimetype = xhr.response.type;
            if (xhr.status === 200 && mimetype !== 'text/html') {
                var header = (xhr.getResponseHeader('Content-Disposition') || '').replace(/;$/, '');
                var filename = header ? contentdisposition.parse(header).parameters.filename : null;
                if (typeof Android != "undefined" && options.data.download) {
                    reader = new FileReader();
                    reader.onload = function() {
                        base64data = reader.result;
                        Android.getFile(base64data, filename, mimetype);
                    };
                    reader.readAsDataURL(xhr.response);
                    return true;
                }
                download(xhr.response, filename, mimetype);
                if (options.success) {
                    options.success();
                }
                return true;
            }
            if (!options.error) {
                return true;
            }
            var decoder = new FileReader();
            decoder.onload = function() {
                var contents = decoder.result;
                var err;
                var doc = new DOMParser().parseFromString(contents, 'text/html');
                var nodes = doc.body.children.length === 0 ? doc.body.childNodes : doc.body.children;
                try {
                    var node = nodes[1] || nodes[0];
                    err = JSON.parse(node.textContent);
                } catch (e) {
                    err = {
                        message: nodes.length > 1 ? nodes[1].textContent : '',
                        data: {
                            name: String(xhr.status),
                            title: nodes.length > 0 ? nodes[0].textContent : '',
                        }
                    }
                }
                options.error(err);
            }
            ;
            decoder.readAsText(xhr.response);
        }
        ;
        xhr.onerror = function() {
            if (options.error) {
                options.error({
                    message: _("Something happened while trying to contact the server, check that the server is online and that you still have a working network connection."),
                    data: {
                        title: _t("Could not connect to the server")
                    }
                });
            }
        }
        ;
        if (options.complete) {
            xhr.onloadend = function() {
                options.complete();
            }
        }
        xhr.send(data);
        return true;
    };
    return ajax;
});