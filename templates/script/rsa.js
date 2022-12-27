const rsa = forge.pki.rsa;

class Cipher {
    #keypair;
    #max_length;
    #separator;
    constructor(separator, generate_keys = true) {
        this.#separator = separator;
        this.#keypair = null;
        if (generate_keys) {
            this.generate_keys();
        }
    }

    static #import_key (key, default_key) {
        if (!key) return default_key;
        if (typeof key !== "string") return key;
        try {
            return forge.pki.publicKeyFromPem(key);
        } catch (e) {
            throw "Invalid PEM key!";
        }
    }

    static #_encrypt(key, text) {
        let ciphertext = key.encrypt(text, 'RSA-OAEP', {
            md: forge.md.sha256.create()
        });
        return forge.util.encode64(ciphertext);
    }

    static #_decrypt(key, encoded) {
        return key.decrypt(forge.util.decode64(encoded), 'RSA-OAEP', {
            md: forge.md.sha256.create()
        });
    }

    generate_keys(length = 2048) {
        if (Math.log2(length) % 1 !== 0 || length < 512 || length > 4096) {
            throw "Key length must be power of two between 512 and 4096!";
        }
        this.#keypair = rsa.generateKeyPair({bits: length, workers: -1});
        this.#max_length = length / 8 - (2 * 256 / 8) - 2;
    }

    get public_key() {
        return forge.pki.publicKeyToPem(this.#keypair.public_key());
    }

    get max_message_length() {
        return this.#max_length;
    }

    encrypt(text, named_args={key: null, chunk_length: null, separator: null, chunk_func: null}) {
        let key = Cipher.#import_key(named_args['key'], this.#keypair ? this.#keypair.publicKey : null);
        if (!key) throw 'Keys are not generated, neither key was provided to function or it was incorrect!';
        let chunk_length = named_args['chunk_length'] ? named_args['chunk_length'] : this.#max_length;
        let separator = named_args['separator'] ? named_args['separator'] : this.#separator;
        let chunk_func = named_args['chunk_func'] ? named_args['chunk_func'] : (to_split, length) => {
            let chunks = [];
            for (let i of range(0, to_split.length, length).slice(0, -1)) {
                chunks.push([to_split.substring(i, i+length), true]);
            }
            return chunks;
        }

        let chunks = chunk_func(text, chunk_length);
        let out_text = "";
        for (let [chunk, encrypt] of chunks) {
            if (encrypt) {
                out_text += Cipher.#_encrypt(key, chunk);
            } else {
                out_text += forge.util.encode64(chunk);
            }
            out_text += separator;
        }

        return out_text.substring(0, out_text.length - 2);
    }

    static static_encrypt(text, key, separator, chunk_length, named_args={chunk_func: null}) {
        key = Cipher.#import_key(key, null);
        chunk_length = parseInt(chunk_length);
        let chunk_func = named_args['chunk_func'] ? named_args['chunk_func'] : (to_split, length) => {
            let chunks = [];
            for (let i of range(0, to_split.length, length).slice(0, -1)) {
                chunks.push([to_split.substring(i, i+length), true]);
            }
            return chunks;
        }
        let chunks = chunk_func(text, chunk_length);
        let out_text = "";
        for (let [chunk, encrypt] of chunks) {
            if (encrypt) {
                out_text += Cipher.#_encrypt(key, chunk);
            } else {
                out_text += forge.util.encode64(chunk);
            }
            out_text += separator;
        }

        return out_text.substring(0, out_text.length - 2);
    }

    decrypt(text, named_args={key: null, separator: null}) {
        let key = Cipher.#import_key(named_args['key'], this.#keypair ? this.#keypair.privateKey : null);
        if (!key) throw 'Keys are not generated, neither key was provided to function or it was incorrect!';
        let separator = named_args['separator'] ? named_args['separator'] : this.#separator;

        let out = "";
        for (let chunk of text.split(separator)) {
            try {
                out += Cipher.#_decrypt(key, chunk);
            } catch (e) {
                out += forge.util.decode64(chunk);
            }
        }

        return out;
    }
}