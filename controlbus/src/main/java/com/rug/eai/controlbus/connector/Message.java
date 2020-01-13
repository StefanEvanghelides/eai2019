package com.rug.eai.controlbus.connector;

public class Message {

    private String name;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    @Override
    public String toString() {
        return "Product{" +
            "name='" + name + '\'' +
           /* ", description='" + description + '\'' +
            ", imageUrl='" + imageUrl + '\'' +
            ", price=" + price +*/
            '}';
    }
}
