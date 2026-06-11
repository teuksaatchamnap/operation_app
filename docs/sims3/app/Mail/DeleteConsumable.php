<?php

namespace App\Mail;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class DeleteConsumable extends Mailable
{
    use Queueable, SerializesModels;
    public $email;
    public $dateapproval;
    public $reason;
    public $manager;
    /**
     * Create a new message instance.
     */
    public function __construct($email,$dateapproval,$reason,$manager)
    {
        $this->email = $email;
        $this->dateapproval = $dateapproval;
        $this->reason = $reason;
        $this->manager = $manager;
    }

    /**
     * Get the message envelope.
     */
    public function envelope(): Envelope
    {
        return new Envelope(
            subject: 'Delete Consumable on '. $this->dateapproval,
        );
    }

    /**
     * Get the message content definition.
     */
    public function content(): Content
    {
        return new Content(
            markdown: 'emails.RequestConsumable.DeleteConsumable',
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
