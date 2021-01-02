const swapBuffer = new ArrayBuffer(4);
const swapView = new DataView(swapBuffer);
export function swap32(value)
{
    swapView.setUint32(0, value, true);
    return swapView.getUint32(0, false);
}


export async function sleep(timeout)
{
    await new Promise(resolve => setTimeout(resolve, timeout));
}


export function hex(value)
{
    return "0x" + value.toString(16);
}


export function choice(array)
{
    return array[randBelow(array.length)];
}


export function random()
{
    return randInt() / 0xFFFFFFFF;
}


const randBuffer = new ArrayBuffer(4);
const randArray = new Uint32Array(randBuffer);
export function randInt()
{
    crypto.getRandomValues(randArray);
    return randArray[0];
}


export function randBelow(limit)
{
    if (limit === undefined) return randInt();

    const threshold = 0x100000000 % limit;
    while (true) {
        const value = randInt();
        if (value >= threshold)
        {
            return value % limit;
        }
    }
}


export function randBetween(start, stop)
{
    if (start === undefined) start = 0
    if (stop === undefined) stop = 0xFFFFFFFF;
    
    return start + randBelow(stop - start);
}


export function randBytes(length)
{
    const buffer = new ArrayBuffer(length);
    const array = new Uint8Array(buffer);
    crypto.getRandomValues(array);
    return buffer;
}


// Array of hex bytes from 00 to ff
const hexBytes = [];
for (let i=0; i < 0xff; i++) {
    hexBytes.push(i.toString(16).padStart(2, "0"));
}

// Returns bytes in hex string form.
export function token(length)
{
    const buffer = randBytes(length);
    const array = new Uint8Array(buffer);
    const result = new Array(length);
    for (let i=0; i < array.length; i++) {
        result[i] = hexBytes[array[i]];
    }
    return result.join("");
}
