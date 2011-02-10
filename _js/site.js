var http = null

//
// TODO:
//  Az osszes fuggvenyt kommentezni
//

/*
 * A html elemet objectumma alakitja es az
 * objectummal ter vissza:
 *
 *  $("resoults").innerHTML = '<p>Take OFF</p>'
 *
 */
function $(element) {
    var ret = null
    if ( document.getElementById && document.getElementById(element) != 'null') {
        ret = document.getElementById(element)
    } else {
        ret = document.getElementsByName(element)
    }
    if ( ret.length == 1 ) ret = ret.item(0)

    return ret
}

/*
 * Elkeri a servertol a search form
 * eredmenyet
 */
this.getURL = function() {
    var post = processForm()
    var timestamp = Number(new Date());
    var boundary = "LogWalker_" + timestamp

    http = new XMLHttpRequest()
    http.open("post", "logwalker.py", true)
    //http.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
    http.setRequestHeader("Content-Type", "multipart/form-data; boundary=" + boundary)
    http.onreadystatechange = responseParser
    http.send("--" + boundary + "\nContent-Disposition: form-data; name=\"data\"\n\n" + post + "\n--" + boundary + "--\n")
}

this.responseParser = function() {
    if (http.readyState == 4 && http.status == 200) {
        $("resoults").innerHTML = parse(http.responseText)
    }
}

this.reviver = function (key, value) {
    var type;
    if (value && typeof value === 'object') {
        type = value.type;
        if (typeof type === 'string' && typeof window[type] === 'function') {
            return new (window[type])(value);
        }
    }
    return value;
}

this.parse = function(jsontext) {
    var htmlString = ''
    var lineStyle = 'dark'
    var j = null
    var jsonParsedObject = JSON.parse(jsontext, reviver)

    for ( j in jsonParsedObject ) {
        /*
         * mezo sorrend:
         * id, datetime, host, facility.priority, tag, message
         */
        if ( typeof jsonParsedObject[j] === 'object' ) {
            var line = null
            var jsonLine = jsonParsedObject[j]
            line  = '<div id="' + lineStyle + '">'
            line += '<div class="' + jsonLine.priority + '">'
            line += '<div class="id">' + jsonLine.id + '.</div>'
            line += '<div class="datetime">' + jsonLine.datetime + '</div>'
            line += '<div class="host" title="' + jsonLine.host + '">' + jsonLine.host + '</div>'
            line += '<div class="level">' + jsonLine.facility + '.' + jsonLine.priority + '</div>'
            line += '<div class="tag">' + jsonLine.tag + '</div>'
            line += '<div class="message" title="' + jsonLine.message + '">' + jsonLine.message + '</div></div></div>'

            if ( lineStyle == 'dark' ) {
                lineStyle = 'light'
            } else if ( lineStyle == 'light' ) {
                lineStyle = 'dark'
            }

            htmlString += line + "\n"
        }
    }

    return htmlString
}

this.flipForm = function() {
    /*
     * Flip the visibility of search form
     */

     if ( $('searchform').style && $('searchform').style.visibility != 'hidden') {
         $('searchform').style.height = '0px'
         $('searchform').style.visibility = 'hidden'
         $('hideicon').src = '_imgs/unhidesearch.gif'

         return
     }

     if ( $('searchform').style && $('searchform').style.visibility != 'visible') {
         $('searchform').style.height = '280px'
         $('searchform').style.visibility = 'visible'
         $('hideicon').src = '_imgs/hidesearch.gif'

         return
     }
}

this.loadForm = function() {
    loadHosts()
    setTimeout(loadTags, 100)
}

this.loadHosts = function() {
    http = new XMLHttpRequest()
    http.open("get", "logwalker.py?getForm=hosts", true)
    http.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
    http.onreadystatechange = hostsFormResponseParser
    http.send(null)
}

this.loadTags = function() {
    http = new XMLHttpRequest()
    http.open("get", "logwalker.py?getForm=tags", true)
    http.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
    http.onreadystatechange = tagsFormResponseParser
    http.send(null)
}

this.hostsFormResponseParser = function() {
    var hosts = http.responseText
    if ( !hosts ) return
    var jsonParsedObject = JSON.parse(hosts, reviver)
    var hostFieldSet = '<legend>Hosts</legend><select size="7" multiple name="hosts">'
    for ( h in jsonParsedObject ) {
        if ( typeof jsonParsedObject[h] === 'object' ) {
            hostFieldSet += '<option value="' + jsonParsedObject[h].host + '">' + jsonParsedObject[h].host + '</option>'
        }
    }
    hostFieldSet += '</select><p><input type="radio" checked name="includeHosts" value="include" /><label>Include</label><input type="radio" name="includeHosts" value="exclude" /><label>Exclude</label></p>'+ "\n"
    $("hosts").innerHTML = hostFieldSet
}

this.tagsFormResponseParser = function() {
    var tags = http.responseText
    if ( !tags ) return
    var jsonParsedObject = JSON.parse(tags, reviver)
    var tagFieldSet = '<legend>Tags</legend><select size="7" multiple name="tags">'
    for ( t in jsonParsedObject ) {
        if ( typeof jsonParsedObject[t] === 'object' ) {
            tagFieldSet += '<option value="' + jsonParsedObject[t].tag + '">' + jsonParsedObject[t].tag + '</option>'
        }
    }
    tagFieldSet += '</select><p><input type="radio" checked name="includeTags" value="include" /><label>Include</label><input type="radio" name="includeTags" value="exclude" /><label>Exclude</label></p>'+ "\n"
    $("tags").innerHTML = tagFieldSet
}

this.formReset = function() {
    $('form').reset()
    return true
}

this.processForm = function() {
    var ret = Array()
    var formElements = document.searchform
    for ( var sF = 1; sF < formElements.length; sF++ ) {
        if ( formElements[sF].name !== undefined && formElements[sF].value !== undefined ) {
            //alert(formElements[sF].name + " " + formElements[sF].value + " " + formElements[sF].type)
            if ( formElements[sF].type == 'select-multiple' && formElements[sF].options.length > 0 ) {
                var elements = Array()
                for ( var e = 0; e < formElements[sF].options.length; e++ ) {
                    if ( formElements[sF].options[e].selected ) {
                        // alert(formElements[sF].options[e].value)
                        elements.push(formElements[sF].options[e].value)
                    }
                }
                ret.push( '{"' + formElements[sF].name + '":' + elements.toSource() + '}' )
            } else if ( ( formElements[sF].type == 'radio' || formElements[sF].type == 'checkbox' ) && formElements[sF].checked ) {
                ret.push( '{"' + formElements[sF].name + '":"' + formElements[sF].value + '"}' )
            } else if ( formElements[sF].type == 'text' && ( formElements[sF].value != '' || formElements[sF].value != undefined ) ) {
                textValue = formElements[sF].value
                textValue = textValue.replace(/"/g, '&quote;')
                textValue = textValue.replace(/'/g, "&#39;")
                textValue = textValue.replace(/>/g, "&gt;")
                textValue = textValue.replace(/</g, "&lt;")
                ret.push( '{"' + formElements[sF].name + '":"' + textValue + '"}' )
            } else if ( formElements[sF].type == 'select-one' ) {
                ret.push( '{"' + formElements[sF].name + '":"' + formElements[sF].value + '"}' )
            }
        }
    }
    //alert('[' + ret.toString() + ']')
    return '[' + ret.toString() + ']'
}
