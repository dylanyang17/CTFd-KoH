(function (definition) {
  // Prefer window over self for add-on scripts. Use self for
  // non-windowed contexts.
  var global = typeof window !== "undefined" ? window : self;

  // Get the `window` object, save the previous KoH_API global
  // and initialize KoH_API as a global.
  var previousKoH_API = global.KoH_API;
  global.KoH_API = definition();

  // Add a noConflict function so KoH_API can be removed from the
  // global namespace.
  global.KoH_API.noConflict = function () {
    global.KoH_API = previousKoH_API;
    return this;
  };
})(function() {
  "use strict";

  function API() {
    this.domain = "/api/v1";
  }

  function serializeQueryParams(parameters) {
    let str = [];
    for (let p in parameters) {
      if (parameters.hasOwnProperty(p)) {
        str.push(
          encodeURIComponent(p) + "=" + encodeURIComponent(parameters[p])
        );
      }
    }
    return str.join("&");
  }

  function mergeQueryParams(parameters, queryParameters) {
    if (parameters.$queryParameters) {
      Object.keys(parameters.$queryParameters).forEach(function(parameterName) {
        let parameter = parameters.$queryParameters[parameterName];
        queryParameters[parameterName] = parameter;
      });
    }
    return queryParameters;
  }

  /**
   * HTTP Request
   * @method
   * @name API#request
   * @param {string} method - http method
   * @param {string} url - url to do request
   * @param {object} parameters
   * @param {object} body - body parameters / object
   * @param {object} headers - header parameters
   * @param {object} queryParameters - querystring parameters
   * @param {object} form - form data object
   * @param {object} deferred - promise object
   */
  API.prototype.request = function(
    method,
    url,
    parameters,
    body,
    headers,
    queryParameters,
    form,
    deferred
  ) {
    const queryParams =
      queryParameters && Object.keys(queryParameters).length
        ? serializeQueryParams(queryParameters)
        : null;
    const urlWithParams = url + (queryParams ? "?" + queryParams : "");

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
        deferred.resolve(body);
      })
      .catch(error => {
        deferred.reject(error);
      });
  };

  /**
   *
   * @method
   * @name API#get_challenge_list
   * @param {object} parameters - method options and parameters
   */
   API.prototype.get_challenge_list = function(parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/challenges";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_challenge_submits
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.challengeId - A Challenge ID
   */
   API.prototype.get_challenge_submits = function(parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/plugins/CTFd-KoH/scoreboard/{challenge_id}/mine";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    if (parameters["challengeId"] === undefined) {
      deferred.reject(new Error("Missing required parameter: challengeId"));
      return deferred.promise;
    }

    path = path.replace("{challenge_id}", parameters["challengeId"]);

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_scoreboard_list
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.challengeId - A Challenge ID
   */
   API.prototype.get_scoreboard_list = function(parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/plugins/CTFd-KoH/scoreboard/{challenge_id}/standings";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    if (parameters["challengeId"] === undefined) {
      deferred.reject(new Error("Missing required parameter: challengeId"));
      return deferred.promise;
    }

    path = path.replace("{challenge_id}", parameters["challengeId"]);

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred
    );

    return deferred.promise;
  };
  /**
   *
   * @method
   * @name API#get_scoreboard_detail
   * @param {object} parameters - method options and parameters
   * @param {string} parameters.challengeId - A Challenge ID
   * @param {string} parameters.count - How many top teams to return
   */
  API.prototype.get_scoreboard_detail = function(parameters) {
    if (parameters === undefined) {
      parameters = {};
    }
    let deferred = Q.defer();
    let domain = this.domain,
      path = "/plugins/CTFd-KoH/scoreboard/{challenge_id}/top/{count}";
    let body = {},
      queryParameters = {},
      headers = {},
      form = {};

    headers["Accept"] = ["application/json"];
    headers["Content-Type"] = ["application/json"];

    if (parameters["count"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: count"));
      return deferred.promise;
    }

    if (parameters["challengeId"] === undefined) {
      deferred.reject(new Error("Missing required  parameter: challengeId"));
      return deferred.promise;
    }

    path = path.replace("{count}", parameters["count"]);
    path = path.replace("{challenge_id}", parameters["challengeId"]);

    queryParameters = mergeQueryParams(parameters, queryParameters);

    this.request(
      "GET",
      domain + path,
      parameters,
      body,
      headers,
      queryParameters,
      form,
      deferred
    );

    return deferred.promise;
  };

  return API;
});
