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

function mergeQueryParams(parameters, queryParameters) {
    if (parameters.$queryParameters) {
        Object.keys(parameters.$queryParameters).forEach(function (parameterName) {
            let parameter = parameters.$queryParameters[parameterName];
            queryParameters[parameterName] = parameter;
        });
    }
    return queryParameters;
}

function loadChals() {
    return new Promise(function (resolve, reject) {
        let parameters = {};
        let domain = "api/v1",
            path = "/admin/challenges";
        let body = {},
            queryParameters = {},
            headers = {},
            form = {};

        headers["Accept"] = ["application/json"];
        headers["Content-Type"] = ["application/json"];

        if (parameters["id"] !== undefined) {
            queryParameters["id"] = parameters["id"];
        }

        path = path.replace("{challenge_id}", parameters["challengeId"]);

        queryParameters = mergeQueryParams(parameters, queryParameters);

        let method = "GET",
            url = domain + path;

        let queryParams =
            queryParameters && Object.keys(queryParameters).length
                ? serializeQueryParams(queryParameters)
                : null;
        let urlWithParams = url + (queryParams ? "?" + queryParams : "");

        if (body && !Object.keys(body).length) {
            body = undefined;
        }

        fetch(urlWithParams, {
            method,
            headers,
            body: JSON.stringify(body)
        })
            .then(response => {
                return response.json();
            })
            .then(body => {
                resolve(body);
            })
            .catch(error => {
                reject(error);
            });

    }).then(response => {
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
