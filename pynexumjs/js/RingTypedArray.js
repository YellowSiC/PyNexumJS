
class RingTypedArray {
    constructor(arrayLength, ArrayType=Uint8Array, value=0){
        this.VERSION = '0.0.0';
        this._unitLength = ArrayType.BYTES_PER_ELEMENT;
        if(arrayLength < 2){
            throw new Error("Invalid arrayLength in <RingBinaryArray>");
        }
        this._arrayLength = arrayLength;
        this._buffer = new ArrayType(arrayLength);
        this._ArrayType = ArrayType;
        this._buffer.fill(value);
        this._startIndex = 0;
        // Endian of browser. Little endian: true / Big endian: false
        this._endian = this._judgeEndian();
    }
    _judgeEndian(){
        let buffer = new ArrayBuffer(2);
        new DataView(buffer).setInt16(0, 256, true);
        return((new Int16Array(buffer)[0]) === 256);
    }

    isLittleEndian(){
        return(this._endian);
    }

    fill(value=0){
        this._buffer.fill(value);
        this._startIndex = 0;
    }

    push(arrayLike){
        let target = new (this._ArrayType)(arrayLike);
        let targetLength = target.length;

        if(targetLength >= this._arrayLength){
            this._buffer.set(target.subarray(targetLength-this._arrayLength));
            this._startIndex = 0;
        }
        else if(this._startIndex+targetLength > this._arrayLength){
            this._buffer.set(target.subarray(0, this._arrayLength-this._startIndex), this._startIndex);
            this._buffer.set(target.subarray(this._arrayLength-this._startIndex));
            this._startIndex = this._startIndex+targetLength-this._arrayLength;
        }
        else{
            this._buffer.set(target, this._startIndex);
            this._startIndex = this._startIndex+targetLength;
        }
        return(true);
    }

    shift(){
        let summary = new (this._ArrayType)(this._arrayLength);
        if(this._startIndex !== 0){
            summary.set(this._buffer.subarray(this._startIndex));
            summary.set(this._buffer.subarray(0, this._startIndex), this._arrayLength-this._startIndex);
        }
        else{
            summary.set(this._buffer);
        }
        return(summary);
    }
    pop(){
        let summary = new (this._ArrayType)(this._arrayLength);
        if(this._startIndex !== 0){
            summary.set(this._buffer.subarray(this._startIndex));
            summary.set(this._buffer.subarray(0, this._startIndex), this._arrayLength-this._startIndex);
        }
        else{
            summary.set(this._buffer);
        }
        return(summary.reverse());
    }
}