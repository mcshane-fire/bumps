#!/bin/python3

ccol = {"Ca" : {'name' : "Caius", 'colours' : ['black', 'lightgreen']},
        "T"  : {'name' : "1st and 3rd", 'colours' : ['darkblue']}, 
        "E"  : {'name' : "Emmanuel", 'colours' : ['blue', 'pink']},
        "TH" : {'name' : "Trinity Hall", 'colours' : ['black', 'white']},
        "D"  : {'name' : "Downing", 'colours' : ['purple']},
        "J"  : {'name' : "Jesus", 'colours' : ['black', 'red']},
        "L"  : {'name' : "LMBC", 'colours' : ['red']},
        "Cu" : {'name' : "Churchill", 'colours' : ['pink']},
        "Cr" : {'name' : "Christ's", 'colours' : ['navy', 'white']},
        "SC" : {'name' : "St Catharine's", 'colours' : ['darkred']},
        "K"  : {'name' : "King's", 'colours' : ['purple', 'white']},
        "Q"  : {'name' : "Queens'", 'colours' : ['green']},
        "Pb" : {'name' : "Pembroke", 'colours' : ['lightblue', 'darkblue']},
        "Ph" : {'name' : "Peterhouse", 'colours' : ['darkblue', 'white']},
        "Cl" : {'name' : "Clare", 'colours' : ['yellow']},
        "CH" : {'name' : "Clare Hall", 'colours' : ['yellow', 'black', 'red']},
        "M"  : {'name' : "Magdalene", 'colours' : ['magenta']},
        "A"  : {'name' : "Addenbrooke's", 'colours' : ['blue']},
        "LC" : {'name' : "Lucy Cavendish", 'colours' : ['blue', 'black']},
        "G"  : {'name' : "Girton", 'colours' : ['green', 'white', 'red', 'white']},
        "F"  : {'name' : "Fitzwilliam", 'colours' : ['red', 'silver']},
        "CC" : {'name' : "Corpus Christi", 'colours' : ['darkred', 'white']},
        "W"  : {'name' : "Wolfson", 'colours' : ['blue', 'yellow']},
        "Dw" : {'name' : "Darwin", 'colours' : ['blue', 'yellow', 'lightblue', 'red']},
        "SE" : {'name' : "St Edmund's", 'colours' : ['blue', 'lightblue', 'white']},
        "HH" : {'name' : "Hughes Hall", 'colours' : ['white', 'blue', 'darkblue']},
        "SS" : {'name' : "Sidney Sussex", 'colours' : ['darkblue', 'red']},
        "S"  : {'name' : "Selwyn", 'colours' : ['lightgray', 'red', 'yellow']},
        "R"  : {'name' : "Robinson", 'colours' : ['blue', 'yellow']},
        "H"  : {'name' : "Homerton", 'colours' : ['lightgray', 'darkblue']},
        "CT" : {'name' : "CCAT", 'colours' : ['black', 'yellow']},
        "N"  : {'name' : "Newnham", 'colours' : ['yellow', 'silver', 'navy']},
        "NH" : {'name' : "New Hall", 'colours' : ['lightgray']},
        "VS" : {'name' : "Vet School", 'colours' : ['blue']},
        "QM" : {'name' : "QMABC", 'colours' : ['purple', 'white']},
        "TC" : {'name' : "Theological Colleges", 'colours' : ['lightgray']},
        "ME" : {'name' : "Murray Edwards", 'colours' : ['lightgray']},
        "AR" : {'name' : "Anglia Ruskin", 'colours' : ['black', 'yellow']},
        "HHL" : {'name' : "Hughes/Lucy", 'colours' : ['white', 'blue', 'darkblue']}}

ocol = {"B" : {'name' : 'Balliol'},
        "Br" : {'name' : 'Brasenose'},
        "Ch" : {'name' : 'Christ Church'},
        "Co" : {'name' : 'Corpus Christi'},
        "E" : {'name' : 'Exeter'},
        "H" : {'name' : 'Hertford'},
        "J" : {'name' : 'Jesus'},
        "K" : {'name' : 'Keble'},
        "L" : {'name' : 'Linacre'},
        "Lc" : {'name' : 'Lincoln'},
        "LM" : {'name' : 'L.M.H.'},
        "Mg" : {'name' : 'Magdalen'},
        "Mf" : {'name' : 'Mansfield'},
        "Mt" : {'name' : 'Merton'},
        "N" : {'name' : 'New College'},
        "O" : {'name' : 'Oriel'},
        "OG" : {'name' : 'Osler-Green'},
        "P" : {'name' : 'Pembroke'},
        "Q" : {'name' : "Queen's"},
        "R" : {'name' : "Regent's Park"},
        "SE" : {'name' : 'S.E.H.'},
        "S" : {'name' : 'Somerville'},
        "SAn" : {'name' : "St Anne's"},
        "SAt" : {'name' : "St Antony's"},
        "SB" : {'name' : "St Benet's Hall"},
        "SC" : {'name' : "St Catherine's"},
        "SHi" : {'name' : "St Hilda's"},
        "SHu" : {'name' : "St Hugh's"},
        "SJ" : {'name' : "St John's"},
        "SP" : {'name' : "St Peter's"},
        "T" : {'name' : 'Trinity'},
        "U" : {'name' : 'University'},
        "Wh" : {'name' : 'Wadham'},
        "Wf" : {'name' : 'Wolfson'},
        "Wt" : {'name' : 'Worcester'}}

sets = {'Summer Eights' : ocol,
        'Lent Bumps' : ccol,
        'May Bumps' : ccol,
        'Torpids' : ocol}

roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"];
