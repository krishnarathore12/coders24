import { useState } from "react";
method: "POST",
body: formData,
});


alert("Document uploaded successfully");
setFile(null);
};


return (
<div className="min-h-screen bg-zinc-50 dark:bg-black flex items-center justify-center">
<div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 gap-6 p-6">


{/* Chatbot Section */}
<Card className="h-[85vh] flex flex-col">
<CardContent className="flex flex-col h-full p-4">
<h2 className="text-xl font-semibold mb-4">RAG Chatbot</h2>


<div className="flex-1 overflow-y-auto space-y-3 mb-4">
{messages.map((msg, i) => (
<div
key={i}
className={`max-w-[75%] rounded-xl px-4 py-2 text-sm ${
msg.role === "user"
? "ml-auto bg-black text-white dark:bg-white dark:text-black"
: "mr-auto bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-100"
}`}
>
{msg.content}
</div>
))}
</div>


<div className="flex gap-2 border-t pt-3">
<Input
placeholder="Ask a question..."
value={input}
onChange={(e) => setInput(e.target.value)}
onKeyDown={(e) => e.key === "Enter" && sendMessage()}
/>
<Button onClick={sendMessage}>
<Send className="h-4 w-4" />
</Button>
</div>
</CardContent>
</Card>


{/* Upload Section */}
<Card className="h-[85vh]">
<CardContent className="p-6 flex flex-col gap-4">
<h2 className="text-xl font-semibold">Document Upload</h2>
<p className="text-sm text-zinc-600 dark:text-zinc-400">
Upload PDFs or text files to power the RAG knowledge base.
</p>


<input
type="file"
accept=".pdf,.txt"
onChange={(e) => setFile(e.target.files?.[0] || null)}
/>


<Button onClick={uploadFile} disabled={!file}>
<Upload className="h-4 w-4 mr-2" /> Upload Document
</Button>
</CardContent>
</Card>


</div>
</div>
);
}
