CTFd._internal.challenge.data = undefined

CTFd._internal.challenge.renderer = CTFd.lib.markdown();


CTFd._internal.challenge.preRender = function () { }

CTFd._internal.challenge.render = function (markdown) {
    return CTFd._internal.challenge.renderer.render(markdown)
}


CTFd._internal.challenge.postRender = function () { }


CTFd._internal.challenge.submit = function (preview) {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
    var submission_file = CTFd.lib.$('#challenge-input')[0].files[0]

    if (submission_file === undefined) {
        var body = {
            'challenge_id': challenge_id,
            'submission': '',
            'content': '',
        }
        var params = {}
        if (preview) {
            params['preview'] = true
        }

        return CTFd.api.post_challenge_attempt(params, body).then(function (response) {
            if (response.status === 429) {
                // User was ratelimited but process response
                return response
            }
            if (response.status === 403) {
                // User is not logged in or CTF is paused.
                return response
            }
            return response
        })
    }

    function file2base64(file) {
        return new Promise(function (resolve, reject) {
            let reader = new FileReader()
            reader.readAsDataURL(file)
            reader.onload = function () {
                resolve(this.result)
            }
        })
    }

    return file2base64(submission_file).then(async function (content) {
        var body = {
            'challenge_id': challenge_id,
            'submission': submission_file.name,
            'content': content,
        }
        var params = {}
        if (preview) {
            params['preview'] = true
        }

        return await CTFd.api.post_challenge_attempt(params, body).then(function (response) {
            if (response.status === 429) {
                // User was ratelimited but process response
                return response
            }
            if (response.status === 403) {
                // User is not logged in or CTF is paused.
                return response
            }
            return response
        })
    })
};

function getSubmits(id) {
    console.log('HELLO');
}
