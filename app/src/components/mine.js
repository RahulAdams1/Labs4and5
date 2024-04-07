class Mine {
    constructor(id, x, y, msn) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.msn = msn;
        this.isActive = true;
        this.img = new Image();
        this.img.src = 'https://play-lh.googleusercontent.com/pHMh7lpyML_1ItqaUnxc3pBzFymwyuv3f_C6Uqq8R5EhBA6qe7dvHhJF_SNAKkvIo2I';
    }
}

export default Mine;