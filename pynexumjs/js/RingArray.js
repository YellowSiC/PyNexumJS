
class RingArray {
    constructor(arrayLength, value=0){
        this.VERSION = '0.0.0';
        if(arrayLength < 2){
            throw new Error("Invalid byteLength in <RingArray>");
        }
        this._length = arrayLength;
        this._buffer = new Array(arrayLength);
        this._buffer.fill(value);
        this._startIndex = 0;
    }
    fill(value=0){
        this._buffer.fill(value);
        this._startIndex = 0;
    }
    push(array){
        let firstLength;
        if(! Array.isArray(array)){
            return(false);
        }
        let array_length = array.length;
        if(array_length < 1){
            return(false);
        }
        else if(array_length >= this._length){
            this._buffer = array.slice(array_length-this._length);
            this._startIndex = 0;
        }
        else{
            if(this._startIndex+array_length > this._length){
                firstLength = this._length-this._startIndex;
                for(let i=0; i<firstLength; ++i){
                    this._buffer[this._startIndex++] = array[i];
                }
                this._startIndex = 0;
                for(let i=firstLength; i<array_length; ++i){
                    this._buffer[this._startIndex++] = array[i];
                }
            }
            else{
                for(let i=0; i<array_length; ++i){
                    this._buffer[this._startIndex++] = array[i];
                }
                if(this._startIndex == this._length){
                    this._startIndex = 0;
                }
            }
        }
        return(true);
    }
    shift(){
        let summary = new Array(this._length);
        let index = 0;
        for(let i=this._startIndex; i< this._length; ++i){
            summary[index++] = this._buffer[i];
        }
        for(let i=0; i<this._startIndex; ++i){
            summary[index++] = this._buffer[i];
        }
        return(summary);
    }
    pop(){
        let summary = new Array(this._length);
        let index = 0;
        for(let i=this._startIndex-1; i>=0; --i){
            summary[index++] = this._buffer[i];
        }
        for(let i=this._length-1; i>=this._startIndex; --i){
            summary[index++] = this._buffer[i];
        }
        return(summary);
    }
}