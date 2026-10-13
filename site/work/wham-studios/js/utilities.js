var d = new Date();
var d = d.getTime();
dynamicScreen();
checkCookie();

function dynamicScreen() {
    $(".sidebar-nav").addClass("collapse");
    if (document.documentElement.clientWidth < 768) {
        $(".mobile").show();
        //        $(".dropdown-toggle").css("width", "90%");
        $(".dropdown-toggle").css("font-size", ".4rem");
        //        $(".search-button").css("width", "90%");
        $(".icon").css("font-size", ".5rem");
        $(".search-input").css("font-size", ".4rem");
        $(".search-input").css("max-width", "130px");
        $(".search-label").css("max-width", "320px");

    } else {
        $(".desktop").show();
        $("#summaryDiv").css("padding-left", "80px");
    }
}

function getCookieObj() {
    cookie = document.cookie;
    console.log(cookie);
    if (cookie) {
        try {
        var obj = JSON.parse(cookie);
        } catch (e) {
            try{
            cookie = "{" +cookie.split('{')[1].split('}')[0] +"}";
            var obj = JSON.parse(cookie);
            }
            catch (e) {
                obj = {
                    "email": "",
                    "sort": "Sort",
                    "filter": "Filter",
                    "search": "",
                    "sessiontime": d,
                    "discount": 0,
                    "total": 0,
                    "orderId": "",
                    "product": "",
                    "cart": [],
                };
                document.cookie = JSON.stringify(obj);
            }
        }
    return obj;
    }
    else{
        return false;
    }
        
}

function checkCookie() {
    cookie = document.cookie;
    if(cookie){
        obj = getCookieObj();
    } else {
        obj = {
            "email": "",
            "sort": "Sort",
            "filter": "Filter",
            "search": "",
            "sessiontime": d,
            "discount": 0,
            "total": 0,
            "orderId": "",
            "product": "",
            "cart": [],
        };
    }
    document.cookie = JSON.stringify(obj);
}

function sendEmail(emailAddress, type, payload) {
    console.log(emailAddress, type, payload);
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
            if (type == "message") {
                window.location.href = "message";
            }
        }
    };
    var params = "emailAddress=" + emailAddress + "&type=" + type + "&payload=" + payload;
    xmlhttp.open("GET", "email.php?" + params, true);
    xmlhttp.send();
}


function timeDisplay(time) {
    var d = new Date();
    var d = d.getTime();
    var ago = d - time;

    if (ago > 31540000000) {
        time = Math.floor(ago / 31540000000);
        if (time > 1)
            time += " years ago";
        else
            time += " year ago";
    } else if (ago > 2628000000) {
        time = Math.floor(ago / 2628000000);
        if (time > 1)
            time += " months ago";
        else
            time += " month ago";
    } else if (ago > 86400000) {
        time = Math.floor(ago / 86400000);
        if (time > 1)
            time += " days ago";
        else
            time += " day ago";
    } else if (ago > 3600000) {
        time = Math.floor(ago / 3600000);
        if (time > 1)
            time += " hours ago";
        else
            time += " hour ago";
    } else if (ago > 60000) {
        time = Math.floor(ago / 60000);
        if (time > 1)
            time += " mins ago";
        else
            time += " min ago";
    } else {
        time = "less than a minute ago";
    }
    return time;
}

function displayPhoto(photoPath, element) {
    storage.ref().child(photoPath).getDownloadURL().then(function (url) {
        element.src = url;
    }).catch(function (error) {
        element.src = "img/robot.jpg";
    });
}


function timeDisplay(time) {
    var d = new Date();
    var d = d.getTime();
    var ago = d - time;

    if (ago > 31540000000) {
        time = Math.floor(ago / 31540000000);
        if (time > 1)
            time += " years ago";
        else
            time += " year ago";
    } else if (ago > 2628000000) {
        time = Math.floor(ago / 2628000000);
        if (time > 1)
            time += " months ago";
        else
            time += " month ago";
    } else if (ago > 86400000) {
        time = Math.floor(ago / 86400000);
        if (time > 1)
            time += " days ago";
        else
            time += " day ago";
    } else if (ago > 3600000) {
        time = Math.floor(ago / 3600000);
        if (time > 1)
            time += " hours ago";
        else
            time += " hour ago";
    } else if (ago > 60000) {
        time = Math.floor(ago / 60000);
        if (time > 1)
            time += " mins ago";
        else
            time += " min ago";
    } else {
        time = "less than a minute ago";
    }
    return time;
}

