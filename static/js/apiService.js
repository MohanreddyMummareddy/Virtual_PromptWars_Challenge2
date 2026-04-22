export default class ApiService {
    constructor(endpoint) {
        this.endpoint = endpoint;
    }

    async fetchChatResponse(message, context) {
        try {
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, context })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Unknown error occurred.');
            }

            return data.response;
        } catch (error) {
            console.error("API Service Error:", error);
            throw new Error("Sorry, I'm having trouble connecting right now.");
        }
    }
}
