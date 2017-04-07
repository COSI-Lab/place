importScripts("/static/sjcl.js");

var HASH_FUNC = sjcl.hash.sha256.hash;
var COUNT_RES = 100000;
var hashes;

function hashSearch(nonce, hardness, minlen) {
	console.log(nonce, hardness, minlen);
	var rand_words = Math.ceil((minlen - sjcl.bitArray.bitLength(nonce)) / 32);
	//console.log("RAND_WORDS:", minlen, sjcl.bitArray.bitLength(nonce), (minlen - sjcl.bitArray.bitLength(nonce)) / 32, rand_words);
	var digest, rand, resp, checkbits, checkamt, good, checkval, idx;
	while(true) {
		rand = sjcl.random.randomWords(rand_words);
		resp = sjcl.bitArray.concat(nonce, rand);
		digest = HASH_FUNC(resp);
		//console.log("RAND", rand, resp, digest);
		hashes += 1;
		if(hashes % COUNT_RES == 0) {
			postMessage({done: false, value: hashes});
		}
		// Probably best put in a function, but inlined here for optimization
		checkbits = hardness;
		good = true;
		idx = 0;
		while(checkbits > 0) {
			checkamt = checkbits;
			if(checkamt > 31) {
				checkamt = 31;
			}
			checkval = sjcl.bitArray.extract(digest, idx, checkamt);
			//console.log("CHECK", digest, idx, checkamt, checkval);
			if(checkval != 0) {
				good = false;
				break;
			}
			idx += checkamt;
			checkbits -= checkamt;
		}
		if(good) {
			console.log("Response:", sjcl.codec.hex.fromBits(resp));
			console.log("Digest:", sjcl.codec.hex.fromBits(digest));
			return resp;
		}
	}
}

onmessage = function(ev) {
	hashes = 0;
	postMessage({done: true, value: hashSearch(ev.data[0], ev.data[1], ev.data[2])});
}
