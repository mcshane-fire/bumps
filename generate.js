var timer = null;
function onKeyUpHandler(){
    timer = setTimeout("generate()", 1000)    
}

function onKeyDownHandler() {
    clearTimeout(timer);
}


var scale = 10;
var font_size = 10;
var abbrev = ["A", "Addenbrooke's",
              "AR", "Anglia Ruskin",
              "Ca", "Caius",
              "CC", "Corpus Christi",
              "CH", "Clare Hall",
              "Cl", "Clare",
              "Cr", "Christ's",
              "CT", "CCAT",
              "Cu", "Churchill",
              "D", "Downing",
              "Dw", "Darwin",
              "E", "Emmanuel",
              "F", "Fitzwilliam",
              "G", "Girton",
              "H", "Homerton",
              "HH", "Hughes Hall",
              "HHL", "Hughes/Lucy",
              "J", "Jesus",
              "K", "King's",
              "L", "LMBC",
              "LC", "Lucy Cavendish",
              "M", "Magdalene",
              "ME", "Murray Edwards",
              "N", "Newnham",
              "NH", "New Hall",
              "Pb", "Pembroke",
              "Ph", "Peterhouse",
              "Q", "Queens'",
              "QM", "QMABC",
              "R", "Robinson",
              "S", "Selwyn",
              "SC", "St Catharine's",
              "SE", "St Edmund's",
              "SS", "Sidney Sussex",
              "T", "1st and 3rd",
              "TC", "Theological Colleges",
              "TH", "Trinity Hall",
              "VS", "Vet School",
              "W", "Wolfson"];

function addcrew(div, crew) {

    var roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"];
    
    if(crew.length === 0)
        return;

    var sh = crew.replace(/[0-9]/, '')
    for(var i=0; i<abbrev.length; i+=2)
    {
        if(sh === abbrev[i])
        {
            var num = crew.substring(abbrev[i].length)
            crew = abbrev[i+1];
            if(num.length > 0)
                crew += " " + roman[parseInt(num)-1];
            break;
        }
    }

    div.push(crew);
}

function draw_crews(divisions, xoff, yoff, align) {
    var ret = "";
    var top = yoff;
    for(var d=0; d<divisions.length; d++) {
        for(var c=0; c<divisions[d].length; c++) {
            top = top + scale;
            ret += '<text fill="black" font-size="'+font_size+'" stroke-width="0" text-anchor="'+align+'" x="'+xoff+'" y="'+(top-2)+'">'+divisions[d][c]+'</text>\n';
        }
    }
    return ret;
}
    
function draw_divisions(event, xoff, yoff, extra) {
    var ret = "";

    var top = yoff + (scale/2);
    for(var div=0; div<event.divisions.length; div++) {
        for(var crew=0; crew<event.divisions[div].length; crew++) {
            var xpos = xoff;
            var ypos = top;
            var points = xpos+","+ypos;
            var c = crew;
            var d = div;
            for(var m=0; m<event.days; m++) {
                var up = event.move[m][d][c];
                xpos += scale;
                ypos -= up * scale;
                points += " "+xpos+","+ypos;
                
                c -= up;
                while(c < 0) {
                    d--;
                    c += event.divisions[d].length;
                }
                while(c >= event.divisions[d].length) {
                    c -= event.divisions[d].length;
                    d++;
                }
            }
            ret += '<polyline fill="none" points="'+points+'"" stroke="black" stroke-width="1" />\n';
            top += scale;
        }
    }

    top = yoff;
    for(var d=0; d<event.divisions.length; d++) {
        ret += '<rect fill="none" height="'+(scale * event.divisions[d].length)+'" stroke="black" ';
        ret += 'width="'+((extra*2)+(scale * event.days))+'" x="'+(xoff-extra)+'" y="'+top+'" />\n';
        top += scale * event.divisions[d].length;
    }

    return ret;
}


function write_svg(event) {

    var right = 80;

    var ret = draw_crews(event.divisions, right-3, 0, 'end');
    ret += draw_crews(event.finish, right + (event.days * scale) + 3, 0, 'start');
    ret += draw_divisions(event, right, 0, right);

    return ret;
}

function process_bump(move, div_num, crew, up) {
    if(crew - up < 1) {
        console.error("Bumping up above the top of the division: div "+div_num+", crew "+crew+", up "+up);
        alert("Bumping up above the top of the division: div "+div_num+", crew "+crew+", up "+up);
        return false;
    }
    if(move[div_num-1][crew-1-up] != 0) {
        console.error("Bumping a crew that has already got a result");
        alert("Bumping a crew that has already got a result");
        return false;
    }
    move[div_num-1][crew-1-up] = -up;
    if(crew > move[div_num-1].length) {
        // sandwich crew, need to find where it started
        for(var p=0; p<move[div_num].length; p++) {
            if(p - move[div_num][p] == 0) {
                move[div_num][p] += up;
                break;
            }
        }
    }
    else
        move[div_num-1][crew-1] = up;

    return true;
}

function process_results(event) {
    if(event.results.length == 0)
        return;
    
    var res = event.results.match(/r|t|u|o[0-9]*|e-?[0-9]*/g);

    var day_num = 0;
    var div_num = 0;
    var crew = 0;
    var move = null;

    for(var i=0; i<res.length; i++) {
        while(move != null && crew <= move[div_num-1].length && crew > 0 && move[div_num-1][crew-1] != 0)
            crew = crew-1;

        if(crew == 0) {
            if(res[i] === 't')
                continue;

            if(div_num <= 1) {
                if(day_num === event.days) {
                    console.error("Run out of days of racing with more results still to go");
                    alert("Run out of days of racing with more results still to go");
                    return;
                }
                move = event.move[day_num];
                day_num += 1;
                div_num = event.divisions.length+1;
            }

            div_num--;
            crew = move[div_num-1].length;
            if(div_num < event.divisions.length)
                crew++; // Sandwich crew
        }

        if(res[i] === 'r') // rowover
            crew--;
        else if(res[i] === 'u') { // bump up
            if(!process_bump(move, div_num, crew, 1))
                return;
            crew -= 2;
        }
        else if(res[i].indexOf('o') == 0) { // overbump
            up = parseInt(res[i].substring(1));
            if(!process_bump(move, div_num, crew, up))
                return;
            crew--;
        }
        else if(res[i].indexOf("e") == 0) { // exact move
            up = parseInt(res[i].substring(1));
            if(crew > move[div_num-1].length)
                move[div_num][0] += up;
            else
                move[div_num-1][crew-1] = up;
            crew--;
        }
        else if(res[i] === 't')
            crew = 0;
    }

    for(var div=0; div < event.divisions.length; div++)
        event.finish.push(new Array(event.divisions[div].length));

    for(var div=0; div < event.divisions.length; div++)
    {
        for(var crew=0; crew < event.divisions[div].length; crew++)
        {
            var d = div;
            var c = crew;
            for(var m=0; m < event.days; m++)
            {
                c = c - event.move[m][d][c];

                while(c < 0) {
                    d--;
                    c += event.move[m][d].length;
                }
                while(c >= event.move[m][d].length)
                {
                    c -= event.move[m][d].length;
                    d++;
                }
            }

            event.finish[d][c] = event.divisions[div][crew];
        }
    }
}

function read_input(event, input) {
    var curdiv = [];
    var inresults = 0;
    var indivision = 0;

    for(var i=0; i<input.length; i++) {
        m = input[i].split(",");
        if (m[0] === 'Set')
            event.set = m[1];
        else if (m[0] === 'Short')
            event.small = m[1];
        else if (m[0] === 'Gender')
            event.gender = m[1];
        else if (m[0] === 'Year')
            event.year = parseInt(m[1]);
        else if (m[0] === 'Days')
            event.days = parseInt(m[1]);
        else if (m[0] === 'Division') {
            indivision = 1;
            if (curdiv.length > 0) {
                event.divisions.push(curdiv)
                curdiv = [];
            }
            for (var j=1; j<m.length; j++) {
                addcrew(curdiv, m[j]);
            }
        }
        else if (m[0] === 'Results') {
            inresults = 1;
            if (curdiv.length > 0) {
                event.divisions.push(curdiv);
                curdiv = [];
            }
            for (var j=1; j<m.length; j++)
                if(m[j].indexOf("#") != 0)
                    event.results += m[j];
        }
        else
        {
            for (var j=0; j<m.length; j++) {
                if (inresults === 1 && m[j].indexOf("#") != 0)
                    event.results += m[j];
                else if(indivision == 1)
                    addcrew(curdiv, m[j]);
            }
        }
    }

    if (curdiv.length > 0)
        event.divisions.push(curdiv);
    
    for(var i=0; i<event.days; i++) {
        var mday = new Array(event.divisions.length);
        for(var d=0; d<event.divisions.length; d++) {
            var mdd = new Array(event.divisions[d].length);
            for(var c=0; c<event.divisions[d].length; c++)
                mdd[c] = 0;
            mday[d] = mdd;
        }
        event.move.push(mday);
    }

    process_results(event);
}


function generate() {
    
    var input = document.getElementById('textid').value.split("\n");
    var event = {set:"Set", small:"Short", gender:"Gender", result : "", year:1970, days:4, divisions : [], results : [], move : [], finish : []};

    read_input(event, input);
    
    var out = "<b>Set:</b> "+event.set;
    out = out + "<br><b>Short:</b> "+event.small;
    out = out + "<br><b>Gender:</b> "+event.gender;
    out = out + "<br><b>Year:</b> "+event.year;
    out = out + "<br><b>Days:</b> "+event.days+"<p>\n";

    out += '<svg baseProfile="tiny" height="100%" version="1.2" width="100%" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">\n';
    out += write_svg(event);
    out += '</svg>\n';

    document.getElementById("chart").innerHTML = out;
}

var str = "<table border=\"0\" cellspacing=\"0\" cellpadding=\"0\">\n";
var colleges =  abbrev.length/2;
var half = Math.round(colleges/2);
for(var i=0; i<half; i++) {
    var c1 = i*2;
    var c2 = (i+half)*2;
    str += "<tr><td>"+abbrev[c1]+"<td width=\"10\"><td>"+abbrev[c1+1];
    if(c2 < abbrev.length)
        str += "<td width=\"40\"><td>"+abbrev[c2]+"<td width=\"10\"><td>"+abbrev[c2+1];
}
str += "</table>\n";
document.getElementById("abbrev").innerHTML = str;

