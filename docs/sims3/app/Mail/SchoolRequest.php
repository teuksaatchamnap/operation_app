<?php

namespace App\Mail;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class SchoolRequest extends Mailable
{
    use Queueable, SerializesModels;
    public $body;
    /**
     * Create a new message instance.
     */
    public function __construct($body)
    {
        $this->body =$body;
    }

    /**
     * Get the message envelope.
     */
    public function envelope(): Envelope
    {
        //if($this->body['ok']=="Over")
        return new Envelope(
            subject: 'Over School Program Request Bottle',
        );
    }

    /**
     * Get the message content definition.
     */
    public function content(): Content
    {
        return new Content(
            markdown: "emails.schoolRequest",
        );
    }

    /**
     * Get the attachments for the message.
     *
     * @return array<int, \Illuminate\Mail\Mailables\Attachment>
     */
    public function attachments(): array
    {
        return [];
    }
}
