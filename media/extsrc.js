// http://whiteposts.com/extsrc
// Released as BSD license
// Author: Slava <whiteposts@gmail.com>

/*

extlib.js is a script that allow to defer loading SCRIPTs in HTML page until
after the page renders. It supports deferred document.write too by creating
SPAN tag after the SCRIPT and then document.write actually set's that tag's
innerHTML.

** HOW TO USE **

<script src="extsrc.js"></script>

<script extsrc="..."></script>   <-- this form is used when external script 
                                     uses document.write

<script asyncsrc="..."></script> <-- this form is used when external script 
                                     doesn't use document.write

Keep in mind that if your external script writes unbalanced tag, like so:
document.write('<a href=#>'), it will be automatically closed (since extsrc
creates a SPAN element after <script> element and assigns '<a href=#>' 
to it as innerHTML to simluate document.write - the browser automatically
will close the unbalanced A: '<a href="#"></a>').


** extsrc.complete **

You can also use extsrc.complete(). 
Note that it runs only after ALL extsrc's are finished loading (NOT when 
document is ready to render).

extsrc.complete(function() { 
    alert('All extsrcs loaded!'); 
});


Thanks to: Kolyaj, arestov, Zitrix, it2days, DriverX, maxpain, dhj, rednaxi,
           Panya, sirus, MiXei4, hyborg and everyone else who helped test and 
           develop.

*/

var extsrc = null;

(function(){
    extsrc = new Object;
    console.log(extsrc.complete_funcs);

    extsrc.complete = function(f) {
        this.complete.funcs.push(f);
    };
    extsrc.complete.funcs = [];



    //document.write('<div id=console></div>');
    //var console = document.getElementById('console');

    var document_write = document.write;
    var document_writeln = document.writeln;
    var buffer = ''; // catching things like d.w('<scr');d.w('ipt></sc');...

    var span = ''; // this is the new element that acts as a placeholder for 
                   // future document.write's
    
    function dumpBuffer() {
        if(buffer && span) {
            document.write = document_write;
            document.writeln = document_writeln;
            var txt = document.createElement('span'); 
            txt.innerHTML = buffer;
            span.appendChild(txt);
            buffer = '';
        };
    };
    
    function runNextScript() {
        dumpBuffer();

        var scripts = document.getElementsByTagName('script');
        for(var i=0;i<scripts.length;i++) {
            // go through all scripts, looking for those with extsrc or asyncsrc
            // attributes. when encountered - set attribute to empty and return
            // from runNextScript.
            // runNextScript will be called when the encountered scripts runs 
            // or fails (onload, onerror (404), readystatechange (good/404)).
        
            var current_script = scripts[i];

            var cur_asyncsrc = current_script.getAttribute('asyncsrc');
            if(cur_asyncsrc) {
                // asyncsrc means script doesn't use document.write - 
                // we can use it all in parallel
                
                current_script.setAttribute('asyncsrc', ''); // don't run 2nd time
                var s = document.createElement('script'); 
                s.async = true;
                s.src = cur_asyncsrc;
                document.getElementsByTagName('head')[0].appendChild(s);
            };
            
            var cur_extsrc = current_script.getAttribute('extsrc');
            if(cur_extsrc) {
                // extsrc means script does use document.write - we can have
                // only one definition of document.write, so load sequentially
                
                current_script.setAttribute('extsrc', ''); // don't run 2nd time
                
                //console.innerHTML += 'start '+extsrc+'<br>'; 

                span = document.createElement('span');
                current_script.parentNode.insertBefore(span, current_script);

                document.write = function(txt) {
                    buffer += txt;
                };

                document.writeln = function(txt) {
                    buffer += txt;
                    buffer += '\n';
                };
                
                var s = document.createElement('script'); 
                s.async = true;
                s.src = cur_extsrc;
                
                if(isIE()) {
                    // IE
                    
                    s.onreadystatechange = function() { 
                        //console.innerHTML += 'readychange '+this.src+' '+this.readyState+'?<br>'; 

                        if(this.readyState == 'loaded' || this.readyState == 'complete') {
                            runNextScript(); 
                        };
                    };
                } else {
                    if((navigator.userAgent.indexOf("Firefox")!=-1) || ('onerror' in s)) {
                        // Firefox
                        
                        s.onload = runNextScript;
                        s.onerror = runNextScript;
                    } else {
                        // Opera
                        
                        s.onload = runNextScript;
                        s.onreadystatechange = runNextScript;
                    };
                };
                document.getElementsByTagName('head')[0].appendChild(s);
                return;            
            };
        };
        dumpBuffer();
        document.write = document_write;
        document.writeln = document_writeln;
        
        for(var i=0; i<extsrc.complete.funcs.length; i++) {
            extsrc.complete.funcs[i]();
        };
    };
    
    function isIE() {
      return /msie/i.test(navigator.userAgent) && !/opera/i.test(navigator.userAgent);
    };
    
    // Below is the code by
    // Dean Edwards/Matthias Miller/John Resig
    // that just acts as window.onload, but in browser-specific way

    function init() {
        if (arguments.callee.done) return;
        arguments.callee.done = true;
        runNextScript();
    };

    /* Mozilla/Firefox/Opera 9 */
    if (document.addEventListener) {
        document.addEventListener("DOMContentLoaded", init, false);
    }

    /* Internet Explorer */
    /*@cc_on @*/
    /*@if (@_win32)
    document.write("<script id=\"__ie_onload\" defer=\"defer\" src=\"javascript:void(0)\"><\/script>");
    var script = document.getElementById("__ie_onload");
    script.onreadystatechange = function() {
        if (this.readyState == "complete") {
	    init();
        }
    };
    /*@end @*/

    /* Safari */
    if (/WebKit/i.test(navigator.userAgent)) { // условие для Safari
        var _timer = setInterval(function() {
	    if (/loaded|complete/.test(document.readyState)) {
	        clearInterval(_timer);
	        init();
	    }
        }, 10);
    }

    /* rest */
    window.onload = init;

})();


