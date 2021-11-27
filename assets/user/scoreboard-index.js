//http://stackoverflow.com/a/2648463 - wizardry!
String.prototype.format = String.prototype.f = function () {
    let s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp("\\{" + i + "\\}", "gm"), arguments[i]);
    }
    return s;
};

//http://stackoverflow.com/a/7616484
String.prototype.hashCode = function () {
    let hash = 0,
        i,
        chr,
        len;
    if (this.length == 0) return hash;
    for (i = 0, len = this.length; i < len; i++) {
        chr = this.charCodeAt(i);
        hash = (hash << 5) - hash + chr;
        hash |= 0; // Convert to 32bit integer
    }
    return hash;
};

function loadChals() {
    return new KoH_API().get_challenge_list().then(function(response) {
        let challenges = response.data.filter(x => x.type == 'koh');

        const $challenges_board = $("#challenges-board");
        $challenges_board.empty();
        const categoryrow = $(
            "" +
            '<div id="koh-row" class="pt-5">' +
            '<div class="category-header col-md-12 mb-3">' +
            "</div>" +
            '<div class="category-challenges col-md-12">' +
            '<div class="challenges-row col-md-12"></div>' +
            "</div>" +
            "</div>"
        );
        $challenges_board.append(categoryrow);

        for (let i = 0; i <= challenges.length - 1; i++) {
            const chalinfo = challenges[i];
            const chalid = chalinfo.name.replace(/ /g, "-").hashCode();
            const chalwrap = $(
                "<div id='{0}' class='col-md-3 d-inline-block'></div>".format(chalid)
            );
            let chalbutton;

            chalbutton = $(
                "<button class='btn btn-dark challenge-button w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'></button>".format(
                    chalinfo.id
                )
            );

            const chalheader = $("<p>{0}</p>".format(chalinfo.name));
            const chalscore = $("<span>{0}</span>".format(chalinfo.value));
            for (let j = 0; j < chalinfo.tags.length; j++) {
                const tag = "tag-" + chalinfo.tags[j].value.replace(/ /g, "-");
                chalwrap.addClass(tag);
            }

            chalbutton.append(chalheader);
            chalbutton.append(chalscore);
            chalwrap.append(chalbutton);

            $("#koh-row")
                .find(".category-challenges > .challenges-row")
                .append(chalwrap);
        }

        $(".challenge-button").click(function (_event) {
            window.location.href = "/koh-scoreboard/" + this.value;
        });
    });
}

loadChals();
