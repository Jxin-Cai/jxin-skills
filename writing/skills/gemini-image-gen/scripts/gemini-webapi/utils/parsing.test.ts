import { describe, expect, test } from 'bun:test';

import { extract_json_from_response } from './parsing.js';

describe('extract_json_from_response', () => {
  test('prefers RPC payload over trailing metrics lines', () => {
    const rpcLine = JSON.stringify([
      ['wrb.fr', null, '[null,["cid","rid"],null,null,[["rcid",["http://googleusercontent.com/image_generation_content/0"]]]]'],
    ]);

    const text = `)]}'

${rpcLine}
["di",69220]
["af.httprm",69220,"7720981798374504844",1]`;

    const parsed = extract_json_from_response(text);
    expect(Array.isArray(parsed)).toBe(true);
    expect(parsed).toEqual(JSON.parse(rpcLine));
  });
});
