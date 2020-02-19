'use strict';

exports.handler = (event, context, callback) => {

  // Get request and request headers
  const request = event.Records[0].cf.request;
  const headers = request.headers;

  // Configure authentication- You can use it for your developers
  const authUser = 'khanhnd3';
  const authPass = 'gErqLSZkZwM';

  // Construct the Basic Auth string
  const authString = 'Basic ' + new Buffer(authUser + ':' + authPass).toString('base64');

  // Configure authentication for the client
  //const authUserForClient = 'kauriru-stg';
  //const authPassForClient = '9KLSZ7Zz2sYAVkwM';
  //const authStringForClient = 'Basic ' + new Buffer(authUserForClient + ':' + authPassForClient).toString('base64');

  // Check wheter the requested resource is allowed or not
  let isAllowedResource = false;
  //Following part will unblock the .png,.svg and .jpg extensions on your cloudfront contained by S3 bucket
  if (request.uri === '/index.html') {
    isAllowedResource = true;
  } else if (/^\/.+(\.png|\.svg|\.jpg)$/.test(request.uri)) {
    isAllowedResource = true;
  }

  // Require Basic authentication
  if (!isAllowedResource && (typeof headers.authorization == 'undefined' || (headers.authorization[0].value != authString))) {
    const body = 'Unauthorized';
    const response = {
      status: '401',
      statusDescription: 'Unauthorized',
      body: body,
      headers: {
        'www-authenticate': [{
          key: 'WWW-Authenticate',
          value: 'Basic'
        }]
      },
    };
    callback(null, response);
  }

  // Continue request processing if authentication passed
  callback(null, request);
};

