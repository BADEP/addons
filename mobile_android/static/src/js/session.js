//odoo.define('web.download', function() {
//    return function download(data, filename, mimetype) {
//        var self = window, defaultMime = "application/octet-stream", mimeType = mimetype || defaultMime, payload = data, url = !filename && !mimetype && payload, anchor = document.createElement("a"), toString = function(a) {
//            return String(a);
//        }, myBlob = (self.Blob || self.MozBlob || self.WebKitBlob || toString), fileName = filename || "download", blob, reader;
//        myBlob = myBlob.call ? myBlob.bind(self) : Blob;
//        if (String(this) === "true") {
//            payload = [payload, mimeType];
//            mimeType = payload[0];
//            payload = payload[1];
//        }
//        if (url && url.length < 2048) {
//            fileName = url.split("/").pop().split("?")[0];
//            anchor.href = url;
//            if (anchor.href.indexOf(url) !== -1) {
//                var ajax = new XMLHttpRequest();
//                ajax.open("GET", url, true);
//                ajax.responseType = 'blob';
//                ajax.onload = function(e) {
//                    download(e.target.response, fileName, defaultMime);
//                }
//                ;
//                setTimeout(function() {
//                    ajax.send();
//                }, 0);
//                return ajax;
//            }
//        }
//        if (/^data:[\w+\-]+\/[\w+\-]+[,;]/.test(payload)) {
//            if (payload.length > (1024 * 1024 * 1.999) && myBlob !== toString) {
//                payload = dataUrlToBlob(payload);
//                mimeType = payload.type || defaultMime;
//            } else {
//                return navigator.msSaveBlob ? navigator.msSaveBlob(dataUrlToBlob(payload), fileName) : saver(payload);
//            }
//        }
//        blob = payload instanceof myBlob ? payload : new myBlob([payload],{
//            type: mimeType
//        });
//        function dataUrlToBlob(strUrl) {
//            var parts = strUrl.split(/[:;,]/)
//              , type = parts[1]
//              , decoder = parts[2] === "base64" ? atob : decodeURIComponent
//              , binData = decoder(parts.pop())
//              , mx = binData.length
//              , i = 0
//              , uiArr = new Uint8Array(mx);
//            for (i; i < mx; ++i)
//                uiArr[i] = binData.charCodeAt(i);
//            return new myBlob([uiArr],{
//                type: type
//            });
//        }
//        function saver(url, winMode) {
//            if ('download'in anchor) {
//                anchor.href = url;
//                anchor.setAttribute("download", fileName);
//                anchor.className = "download-js-link";
//                anchor.innerHTML = "downloading...";
//                anchor.style.display = "none";
//                document.body.appendChild(anchor);
//                setTimeout(function() {
//                    anchor.click();
//                    document.body.removeChild(anchor);
//                    if (winMode === true) {
//                        setTimeout(function() {
//                            self.URL.revokeObjectURL(anchor.href);
//                        }, 250);
//                    }
//                }, 66);
//                return true;
//            }
//            if (/(Version)\/(\d+)\.(\d+)(?:\.(\d+))?.*Safari\//.test(navigator.userAgent)) {
//                url = url.replace(/^data:([\w\/\-+]+)/, defaultMime);
//                if (!window.open(url)) {
//                    if (confirm("Displaying New Document\n\nUse Save As... to download, then click back to return to this page.")) {
//                        location.href = url;
//                    }
//                }
//                return true;
//            }
//            var f = document.createElement("iframe");
//            document.body.appendChild(f);
//            if (!winMode) {
//                url = "data:" + url.replace(/^data:([\w\/\-+]+)/, defaultMime);
//            }
//            f.src = url;
//            setTimeout(function() {
//                document.body.removeChild(f);
//            }, 333);
//        }
//        if (navigator.msSaveBlob) {
//            return navigator.msSaveBlob(blob, fileName);
//        }
//        if (self.URL) {
//            saver(self.URL.createObjectURL(blob), true);
//        } else {
//            if (typeof blob === "string" || blob.constructor === toString) {
//                try {
//                    return saver("data:" + mimeType + ";base64," + self.btoa(blob));
//                } catch (y) {
//                    return saver("data:" + mimeType + "," + encodeURIComponent(blob));
//                }
//            }
//            reader = new FileReader();
//            reader.onload = function() {
//                saver(this.result);
//            }
//            ;
//            reader.readAsDataURL(blob);
//        }
//        return true;
//    }
//    ;
//});
//;

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
console.log('Android: return session');
return ajax;
});