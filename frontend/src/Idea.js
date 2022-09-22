export const Type = {
    CHILDREN: 0, PREDICTIONS: 1, IMAGES: 2
};

export default class Idea {
    constructor(summary, input, parent, children = [], type) {
        this.summary = summary;
        this.input = input;
        this.parent = parent;
        this.children = children;
        this.type = type;
    }

    static fromData(data) {
        return new Idea(data.summary, data.input, data.parent, data.children, data.type);
    }

    addChild(child) {
        this.children.push(child);
    }
}